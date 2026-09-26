// Package fixture reads the checked-in Lite synthetic sources.
package fixture

import (
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"sort"
)

var softwareSources = []string{"crm", "jira", "slack", "meetings"}

// Record is one raw fixture object plus the source name taken from the file.
type Record struct {
	Source string
	Object json.RawMessage
}

// Bundle is the software data directory plus the manufacturing pack.
type Bundle struct {
	Cases   []json.RawMessage
	Records []Record
}

// Load reads data/*.json and domain_packs/manufacturing/*.json under root.
func Load(root string) (Bundle, error) {
	var bundle Bundle
	softwareCases, err := readArray(filepath.Join(root, "data", "cases.json"))
	if err != nil {
		return Bundle{}, err
	}
	bundle.Cases = append(bundle.Cases, softwareCases...)
	for _, source := range softwareSources {
		if err := appendSource(&bundle, filepath.Join(root, "data", source+".json"), source); err != nil {
			return Bundle{}, err
		}
	}

	pack := filepath.Join(root, "domain_packs", "manufacturing")
	info, err := os.Stat(pack)
	if err != nil || !info.IsDir() {
		return Bundle{}, errors.New("manufacturing pack not found")
	}
	manufacturingCases, err := readArray(filepath.Join(pack, "cases.json"))
	if err != nil {
		return Bundle{}, err
	}
	bundle.Cases = append(bundle.Cases, manufacturingCases...)

	paths, err := filepath.Glob(filepath.Join(pack, "*.json"))
	if err != nil {
		return Bundle{}, err
	}
	sort.Strings(paths)
	for _, path := range paths {
		if filepath.Base(path) == "cases.json" {
			continue
		}
		if err := appendSource(&bundle, path, stem(path)); err != nil {
			return Bundle{}, err
		}
	}
	return bundle, nil
}

func appendSource(bundle *Bundle, path, source string) error {
	objects, err := readArray(path)
	if err != nil {
		return err
	}
	for _, object := range objects {
		bundle.Records = append(bundle.Records, Record{Source: source, Object: object})
	}
	return nil
}

func readArray(path string) ([]json.RawMessage, error) {
	name := filepath.Base(path)
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("read %s: file unavailable", name)
	}
	if !json.Valid(data) {
		return nil, fmt.Errorf("parse %s: invalid JSON", name)
	}
	var items []json.RawMessage
	if err := json.Unmarshal(data, &items); err != nil {
		return nil, fmt.Errorf("parse %s: expected a JSON array", name)
	}
	return items, nil
}

func stem(path string) string {
	base := filepath.Base(path)
	return base[:len(base)-len(filepath.Ext(base))]
}
