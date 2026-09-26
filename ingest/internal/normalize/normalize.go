// Package normalize turns fixture objects into Atlas evidence documents.
package normalize

import (
	"encoding/json"
	"errors"
	"fmt"
	"strings"
	"time"

	"mulanouslite/ingest/internal/fixture"
	"mulanouslite/ingest/internal/model"
)

var semanticSources = map[string]struct{}{
	"slack":    {},
	"meetings": {},
	"quality":  {},
}

// Result is the upsert payload. Skipped counts records that were not usable.
type Result struct {
	Cases    []model.CaseDocument
	Evidence []model.EvidenceDocument
	Skipped  int
}

type caseJSON struct {
	ID        string `json:"id"`
	Domain    string `json:"domain"`
	Pattern   string `json:"pattern"`
	Account   string `json:"account"`
	AccountID string `json:"account_id"`
	Claim     string `json:"claim"`
	Urgency   string `json:"urgency"`
}

type evidenceJSON struct {
	ID         string          `json:"id"`
	AccountID  string          `json:"account_id"`
	Title      string          `json:"title"`
	Text       *string         `json:"text"`
	Body       *string         `json:"body"`
	ObservedAt *string         `json:"observed_at"`
	Facts      json.RawMessage `json:"facts"`
}

// Build assigns evidence ids, domains, and retrieval class. It does not embed.
func Build(bundle fixture.Bundle) (Result, error) {
	var result Result
	domains := map[string]string{}
	for _, raw := range bundle.Cases {
		doc, accountID, domain, err := decodeCase(raw, len(result.Cases))
		if err != nil {
			result.Skipped++
			continue
		}
		domains[accountID] = domain
		result.Cases = append(result.Cases, doc)
	}
	if len(result.Cases) == 0 {
		return Result{}, errors.New("no cases loaded")
	}

	seen := map[string]struct{}{}
	for _, record := range bundle.Records {
		doc, err := decodeEvidence(record, domains)
		if err != nil {
			result.Skipped++
			continue
		}
		if _, ok := seen[doc.ID]; ok {
			result.Skipped++
			continue
		}
		seen[doc.ID] = struct{}{}
		result.Evidence = append(result.Evidence, doc)
	}
	if len(result.Evidence) == 0 {
		return Result{}, errors.New("no evidence loaded")
	}
	return result, nil
}

func decodeCase(raw json.RawMessage, order int) (model.CaseDocument, string, string, error) {
	var seed caseJSON
	if err := json.Unmarshal(raw, &seed); err != nil {
		return model.CaseDocument{}, "", "", err
	}
	seed.ID = strings.TrimSpace(seed.ID)
	seed.Domain = strings.TrimSpace(seed.Domain)
	seed.Pattern = strings.TrimSpace(seed.Pattern)
	seed.Account = strings.TrimSpace(seed.Account)
	seed.AccountID = strings.TrimSpace(seed.AccountID)
	seed.Claim = strings.TrimSpace(seed.Claim)
	seed.Urgency = strings.TrimSpace(seed.Urgency)
	if seed.ID == "" || seed.Pattern == "" || seed.Account == "" || seed.AccountID == "" || seed.Claim == "" || seed.Urgency == "" {
		return model.CaseDocument{}, "", "", errors.New("missing case fields")
	}
	if seed.Domain != "software" && seed.Domain != "manufacturing" && seed.Domain != "logistics" {
		return model.CaseDocument{}, "", "", errors.New("unknown domain")
	}
	return model.CaseDocument{
		ID:          seed.ID,
		Domain:      seed.Domain,
		Pattern:     seed.Pattern,
		Account:     seed.Account,
		AccountID:   seed.AccountID,
		Claim:       seed.Claim,
		Urgency:     seed.Urgency,
		IngestOrder: order,
	}, seed.AccountID, seed.Domain, nil
}

func decodeEvidence(record fixture.Record, domains map[string]string) (model.EvidenceDocument, error) {
	var seed evidenceJSON
	if err := json.Unmarshal(record.Object, &seed); err != nil {
		return model.EvidenceDocument{}, err
	}
	sourceID := strings.TrimSpace(seed.ID)
	accountID := strings.TrimSpace(seed.AccountID)
	title := strings.TrimSpace(seed.Title)
	body := bodyText(seed)
	if sourceID == "" || accountID == "" || title == "" || body == "" || strings.TrimSpace(record.Source) == "" {
		return model.EvidenceDocument{}, errors.New("missing evidence fields")
	}
	facts, err := parseFacts(seed.Facts)
	if err != nil {
		return model.EvidenceDocument{}, err
	}
	domain := domains[accountID]
	if domain == "" {
		domain = "software"
	}
	return model.EvidenceDocument{
		ID:             record.Source + ":" + sourceID,
		Source:         record.Source,
		SourceRecordID: sourceID,
		AccountID:      accountID,
		Domain:         domain,
		Title:          title,
		Body:           body,
		ObservedAt:     keepTimestamp(seed.ObservedAt),
		RetrievalClass: retrievalClass(record.Source),
		Facts:          facts,
		Embedding:      nil,
	}, nil
}

func bodyText(seed evidenceJSON) string {
	if seed.Body != nil {
		return strings.TrimSpace(*seed.Body)
	}
	if seed.Text != nil {
		return strings.TrimSpace(*seed.Text)
	}
	return ""
}

func parseFacts(raw json.RawMessage) (map[string]string, error) {
	if len(raw) == 0 || string(raw) == "null" {
		return map[string]string{}, nil
	}
	var fields map[string]json.RawMessage
	if err := json.Unmarshal(raw, &fields); err != nil {
		return nil, errors.New("facts must be an object of strings")
	}
	facts := make(map[string]string, len(fields))
	for key, value := range fields {
		var text string
		if err := json.Unmarshal(value, &text); err != nil {
			return nil, fmt.Errorf("fact %s is not a string", key)
		}
		facts[key] = text
	}
	return facts, nil
}

func retrievalClass(source string) string {
	if _, ok := semanticSources[source]; ok {
		return "semantic"
	}
	return "structured"
}

func keepTimestamp(value *string) *string {
	if value == nil {
		return nil
	}
	text := strings.TrimSpace(*value)
	if text == "" {
		return nil
	}
	parsed, err := time.Parse(time.RFC3339Nano, text)
	if err != nil {
		return nil
	}
	_, offset := parsed.Zone()
	if offset != 0 {
		return nil
	}
	kept := text
	return &kept
}
