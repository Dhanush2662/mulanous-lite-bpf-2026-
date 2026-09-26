package normalize

import (
	"encoding/json"
	"path/filepath"
	"runtime"
	"testing"

	"go.mongodb.org/mongo-driver/bson"

	"mulanouslite/ingest/internal/fixture"
	"mulanouslite/ingest/internal/model"
)

func TestRepoFixturesMatchThePythonEvidenceShape(t *testing.T) {
	bundle := loadRepo(t)
	result, err := Build(bundle)
	if err != nil {
		t.Fatal(err)
	}
	if result.Skipped != 0 {
		t.Fatalf("skipped = %d", result.Skipped)
	}
	if len(result.Cases) != 4 {
		t.Fatalf("cases = %d", len(result.Cases))
	}
	if len(result.Evidence) != 28 {
		t.Fatalf("evidence = %d", len(result.Evidence))
	}
	if result.Cases[0].ID != "acme-sso-rollout" || result.Cases[0].Domain != "software" || result.Cases[0].IngestOrder != 0 {
		t.Fatalf("first case = %#v", result.Cases[0])
	}
	orion := result.Cases[3]
	if orion.ID != "orion-order-5000" || orion.Domain != "manufacturing" || orion.IngestOrder != 3 {
		t.Fatalf("orion = %#v", orion)
	}

	jira := findEvidence(t, result.Evidence, "jira:JIRA-101")
	if jira.RetrievalClass != "structured" || jira.Embedding != nil || jira.SourceRecordID != "JIRA-101" {
		t.Fatalf("jira = %#v", jira)
	}
	slack := findEvidence(t, result.Evidence, "slack:SLACK-411")
	if slack.RetrievalClass != "semantic" || slack.ObservedAt != nil || slack.Domain != "software" {
		t.Fatalf("slack = %#v", slack)
	}
	inventory := findEvidence(t, result.Evidence, "inventory:ORION-MAT-441")
	if inventory.RetrievalClass != "structured" || inventory.Domain != "manufacturing" {
		t.Fatalf("inventory class/domain = %#v", inventory)
	}
	if inventory.Facts["on_hand_qty"] != "1200" || inventory.Facts["status"] != "short" {
		t.Fatalf("inventory facts = %#v", inventory.Facts)
	}
	if inventory.Embedding != nil {
		t.Fatal("structured inventory must not carry an embedding")
	}
	quality := findEvidence(t, result.Evidence, "quality:ORION-QA-17")
	if quality.RetrievalClass != "semantic" || quality.Embedding != nil {
		t.Fatalf("quality = %#v", quality)
	}
	assertBSONKeys(t, inventory)
}

func TestInvalidRowsAreSkipped(t *testing.T) {
	bundle := fixture.Bundle{
		Cases: []json.RawMessage{
			json.RawMessage(`{"id":"acme-sso-rollout","domain":"software","pattern":"customer_commitment_intervention","account":"Acme","account_id":"acme-001","claim":"SSO rollout blocked","urgency":"today"}`),
			json.RawMessage(`{"id":"","domain":"software"}`),
		},
		Records: []fixture.Record{
			{Source: "jira", Object: json.RawMessage(`{"id":"JIRA-1","account_id":"acme-001","title":"Open","text":"remains open","observed_at":"not-a-time"}`)},
			{Source: "jira", Object: json.RawMessage(`{"id":"JIRA-1","account_id":"acme-001","title":"Duplicate","text":"remains open"}`)},
			{Source: "slack", Object: json.RawMessage(`{"id":"S-1","account_id":"acme-001","title":"Note","text":"   "}`)},
			{Source: "inventory", Object: json.RawMessage(`{"id":"MAT-1","account_id":"missing","title":"Qty","text":"1200","facts":{"on_hand_qty":1200}}`)},
			{Source: "quality", Object: json.RawMessage(`{"id":"Q-1","account_id":"acme-001","title":"Hold","body":"quality hold","observed_at":"2026-09-25T13:00:00+02:00"}`)},
		},
	}
	result, err := Build(bundle)
	if err != nil {
		t.Fatal(err)
	}
	if result.Skipped != 4 {
		t.Fatalf("skipped = %d", result.Skipped)
	}
	if len(result.Evidence) != 2 {
		t.Fatalf("evidence = %#v", result.Evidence)
	}
	jira := findEvidence(t, result.Evidence, "jira:JIRA-1")
	if jira.ObservedAt != nil {
		t.Fatalf("invalid timestamp kept: %#v", jira.ObservedAt)
	}
	quality := findEvidence(t, result.Evidence, "quality:Q-1")
	if quality.ObservedAt != nil || quality.RetrievalClass != "semantic" {
		t.Fatalf("quality = %#v", quality)
	}
	unknown := findEvidence(t, result.Evidence, "jira:JIRA-1")
	if unknown.Domain != "software" {
		t.Fatalf("domain = %s", unknown.Domain)
	}
}

func loadRepo(t *testing.T) fixture.Bundle {
	t.Helper()
	_, file, _, ok := runtime.Caller(0)
	if !ok {
		t.Fatal("caller")
	}
	root := filepath.Clean(filepath.Join(filepath.Dir(file), "..", "..", ".."))
	bundle, err := fixture.Load(root)
	if err != nil {
		t.Fatal(err)
	}
	return bundle
}

func findEvidence(t *testing.T, records []model.EvidenceDocument, id string) model.EvidenceDocument {
	t.Helper()
	for _, record := range records {
		if record.ID == id {
			return record
		}
	}
	t.Fatalf("missing %s", id)
	return model.EvidenceDocument{}
}

func assertBSONKeys(t *testing.T, doc model.EvidenceDocument) {
	t.Helper()
	raw, err := bson.Marshal(doc)
	if err != nil {
		t.Fatal(err)
	}
	var fields bson.M
	if err := bson.Unmarshal(raw, &fields); err != nil {
		t.Fatal(err)
	}
	required := []string{
		"id",
		"source",
		"source_record_id",
		"account_id",
		"domain",
		"title",
		"body",
		"observed_at",
		"retrieval_class",
		"facts",
		"embedding",
	}
	for _, key := range required {
		if _, ok := fields[key]; !ok {
			t.Fatalf("bson document missing %s", key)
		}
	}
	if fields["embedding"] != nil {
		t.Fatalf("embedding = %#v", fields["embedding"])
	}
}
