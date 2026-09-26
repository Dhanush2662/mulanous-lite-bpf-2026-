// Package model is the Atlas document shape the Python assembler reads.
// Field names match the Python evidence store. This package is fresh Lite code.
package model

// CaseDocument is one row in the cases collection.
type CaseDocument struct {
	ID          string `bson:"id" json:"id"`
	Domain      string `bson:"domain" json:"domain"`
	Pattern     string `bson:"pattern" json:"pattern"`
	Account     string `bson:"account" json:"account"`
	AccountID   string `bson:"account_id" json:"account_id"`
	Claim       string `bson:"claim" json:"claim"`
	Urgency     string `bson:"urgency" json:"urgency"`
	IngestOrder int    `bson:"ingest_order" json:"ingest_order"`
}

// EvidenceDocument is one row in the evidence collection.
// Embedding is null. The Python process fills semantic vectors on read.
type EvidenceDocument struct {
	ID             string            `bson:"id" json:"id"`
	Source         string            `bson:"source" json:"source"`
	SourceRecordID string            `bson:"source_record_id" json:"source_record_id"`
	AccountID      string            `bson:"account_id" json:"account_id"`
	Domain         string            `bson:"domain" json:"domain"`
	Title          string            `bson:"title" json:"title"`
	Body           string            `bson:"body" json:"body"`
	ObservedAt     *string           `bson:"observed_at" json:"observed_at"`
	RetrievalClass string            `bson:"retrieval_class" json:"retrieval_class"`
	Facts          map[string]string `bson:"facts" json:"facts"`
	Embedding      []float64         `bson:"embedding" json:"embedding"`
}
