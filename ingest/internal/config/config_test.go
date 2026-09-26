package config

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestResolveURIRequiresAValue(t *testing.T) {
	_, err := ResolveURI("  ", map[string]string{})
	if err == nil {
		t.Fatal("expected an error when MONGODB_URI is empty")
	}
	if !strings.Contains(err.Error(), "MONGODB_URI is required") {
		t.Fatalf("error = %q", err)
	}
}

func TestResolveURIPrefersExplicitValue(t *testing.T) {
	got, err := ResolveURI("mongodb://from-env", map[string]string{"MONGODB_URI": "mongodb://from-file"})
	if err != nil {
		t.Fatal(err)
	}
	if got != "mongodb://from-env" {
		t.Fatalf("uri = %q", got)
	}
}

func TestResolveURIUsesDotEnvWhenExplicitIsEmpty(t *testing.T) {
	got, err := ResolveURI("", map[string]string{"MONGODB_URI": "mongodb://from-file"})
	if err != nil {
		t.Fatal(err)
	}
	if got != "mongodb://from-file" {
		t.Fatalf("uri = %q", got)
	}
}

func TestResolveDatabaseDefaults(t *testing.T) {
	if got := ResolveDatabase("", map[string]string{}); got != "mulanous_lite" {
		t.Fatalf("database = %q", got)
	}
	if got := ResolveDatabase("", map[string]string{"MONGODB_DB": "demo"}); got != "demo" {
		t.Fatalf("database = %q", got)
	}
}

func TestLoadDotEnvIgnoresCommentsAndMissingFile(t *testing.T) {
	missing, err := LoadDotEnv(filepath.Join(t.TempDir(), "nope"))
	if err != nil {
		t.Fatal(err)
	}
	if len(missing) != 0 {
		t.Fatalf("missing file returned %#v", missing)
	}

	path := filepath.Join(t.TempDir(), ".env")
	body := "# comment\n\nMONGODB_URI=mongodb://example\nMONGODB_DB=\"mulanous_lite\"\n"
	if err := os.WriteFile(path, []byte(body), 0o600); err != nil {
		t.Fatal(err)
	}
	values, err := LoadDotEnv(path)
	if err != nil {
		t.Fatal(err)
	}
	if values["MONGODB_URI"] != "mongodb://example" {
		t.Fatalf("uri = %q", values["MONGODB_URI"])
	}
	if values["MONGODB_DB"] != "mulanous_lite" {
		t.Fatalf("db = %q", values["MONGODB_DB"])
	}
}
