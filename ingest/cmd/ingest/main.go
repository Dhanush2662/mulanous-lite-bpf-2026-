// Command ingest loads Lite fixtures and upserts them into MongoDB Atlas.
package main

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"time"

	"mulanouslite/ingest/internal/atlas"
	"mulanouslite/ingest/internal/config"
	"mulanouslite/ingest/internal/fixture"
	"mulanouslite/ingest/internal/normalize"
)

func main() {
	if err := run(); err != nil {
		fmt.Fprintf(os.Stderr, "ingest: %s\n", err)
		os.Exit(1)
	}
}

func run() error {
	root, err := findRepoRoot()
	if err != nil {
		return err
	}
	dotenv, err := config.LoadDotEnv(filepath.Join(root, ".env"))
	if err != nil {
		return fmt.Errorf("read .env failed")
	}
	uri, err := config.ResolveURI(os.Getenv("MONGODB_URI"), dotenv)
	if err != nil {
		return err
	}
	database := config.ResolveDatabase(os.Getenv("MONGODB_DB"), dotenv)
	bundle, err := fixture.Load(root)
	if err != nil {
		return err
	}
	normalized, err := normalize.Build(bundle)
	if err != nil {
		return err
	}
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	if err := atlas.Upsert(ctx, uri, database, normalized.Cases, normalized.Evidence); err != nil {
		return err
	}
	fmt.Printf(
		"ingest: upserted cases=%d evidence=%d skipped=%d database=%s\n",
		len(normalized.Cases),
		len(normalized.Evidence),
		normalized.Skipped,
		database,
	)
	return nil
}

func findRepoRoot() (string, error) {
	dir, err := os.Getwd()
	if err != nil {
		return "", err
	}
	for {
		info, statErr := os.Stat(filepath.Join(dir, "data", "cases.json"))
		if statErr == nil && !info.IsDir() {
			return dir, nil
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			return "", fmt.Errorf("could not find data/cases.json; run from the repository")
		}
		dir = parent
	}
}
