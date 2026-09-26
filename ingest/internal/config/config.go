// Package config resolves ingest settings. It never prints secret values.
package config

import (
	"bufio"
	"errors"
	"os"
	"strings"
)

const defaultDatabase = "mulanous_lite"

// ResolveURI returns the Atlas URI. An explicit environment value wins over .env.
func ResolveURI(explicit string, dotenv map[string]string) (string, error) {
	uri := strings.TrimSpace(explicit)
	if uri == "" {
		uri = strings.TrimSpace(dotenv["MONGODB_URI"])
	}
	if uri == "" {
		return "", errors.New("MONGODB_URI is required. Set it in the environment or .env. Ingest does not start without Atlas")
	}
	return uri, nil
}

// ResolveDatabase returns MONGODB_DB or the Lite default.
func ResolveDatabase(explicit string, dotenv map[string]string) string {
	name := strings.TrimSpace(explicit)
	if name == "" {
		name = strings.TrimSpace(dotenv["MONGODB_DB"])
	}
	if name == "" {
		return defaultDatabase
	}
	return name
}

// LoadDotEnv reads KEY=VALUE lines. A missing file is an empty map.
func LoadDotEnv(path string) (map[string]string, error) {
	file, err := os.Open(path)
	if errors.Is(err, os.ErrNotExist) {
		return map[string]string{}, nil
	}
	if err != nil {
		return nil, err
	}
	defer file.Close()

	values := map[string]string{}
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		key, value, ok := parseEnvLine(scanner.Text())
		if !ok {
			continue
		}
		values[key] = value
	}
	if err := scanner.Err(); err != nil {
		return nil, err
	}
	return values, nil
}

func parseEnvLine(line string) (string, string, bool) {
	text := strings.TrimSpace(line)
	if text == "" || strings.HasPrefix(text, "#") {
		return "", "", false
	}
	key, value, ok := strings.Cut(text, "=")
	if !ok {
		return "", "", false
	}
	key = strings.TrimSpace(key)
	value = strings.TrimSpace(value)
	value = strings.Trim(value, `"'`)
	if key == "" {
		return "", "", false
	}
	return key, value, true
}
