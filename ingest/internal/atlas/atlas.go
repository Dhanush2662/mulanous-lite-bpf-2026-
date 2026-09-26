// Package atlas upserts normalized documents. It does not log the URI.
package atlas

import (
	"context"
	"errors"
	"strings"
	"time"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"go.mongodb.org/mongo-driver/mongo/readpref"

	"mulanouslite/ingest/internal/model"
)

// Upsert writes cases and evidence by id. A blank URI or a failed ping is an error.
func Upsert(
	ctx context.Context,
	uri string,
	database string,
	cases []model.CaseDocument,
	evidence []model.EvidenceDocument,
) error {
	if strings.TrimSpace(uri) == "" {
		return errors.New("MONGODB_URI is required")
	}
	client, err := mongo.Connect(ctx, options.Client().
		ApplyURI(uri).
		SetServerSelectionTimeout(2*time.Second).
		SetConnectTimeout(2*time.Second))
	if err != nil {
		return errors.New("atlas unavailable")
	}
	defer disconnect(client)

	if err := client.Ping(ctx, readpref.Primary()); err != nil {
		return errors.New("atlas unavailable")
	}
	if err := replaceEach(ctx, client.Database(database).Collection("cases"), cases); err != nil {
		return err
	}
	return replaceEvidence(ctx, client.Database(database).Collection("evidence"), evidence)
}

func replaceEach(ctx context.Context, collection *mongo.Collection, cases []model.CaseDocument) error {
	for _, item := range cases {
		_, err := collection.ReplaceOne(ctx, bson.M{"id": item.ID}, item, options.Replace().SetUpsert(true))
		if err != nil {
			return errors.New("atlas unavailable")
		}
	}
	return nil
}

func replaceEvidence(ctx context.Context, collection *mongo.Collection, evidence []model.EvidenceDocument) error {
	for _, item := range evidence {
		_, err := collection.ReplaceOne(ctx, bson.M{"id": item.ID}, item, options.Replace().SetUpsert(true))
		if err != nil {
			return errors.New("atlas unavailable")
		}
	}
	return nil
}

func disconnect(client *mongo.Client) {
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()
	_ = client.Disconnect(ctx)
}
