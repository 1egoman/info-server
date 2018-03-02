package main

import (
  "fmt"
)

type CalculateMethod func() (interface{}, error)

func CalculateAll(data map[string]interface{}, methods map[string]CalculateMethod) error {
  for key, fn := range methods {
    value, err := fn()
    if err != nil {
      data[key] = value
    } else {
      return err
    }
  }

  return nil
}

type DatumKind string

const (
  TEXT DatumKind = "TEXT"
  IMAGE = "IMAGE"
  VIDEO_FRAME = "VIDEO_FRAME"
)

var currentDatumIndex int = 0

type Datum interface {
  Kind() DatumKind
  Build()

  Index() int
  Next() *Datum
  Previous() *Datum

  Calculate() error
}





type TextDatum struct {
  kind DatumKind

  index int
  next *Datum
  prev *Datum

  data map[string]interface{}
}

func (t *TextDatum) Kind() DatumKind { return t.kind }
func (t *TextDatum) Build(input interface{}, data map[string]interface{}) {
  t.data = map[string]interface{}{}
}
func (t *TextDatum) Index() int { return t.index }
func (t *TextDatum) Next() *Datum { return t.next }
func (t *TextDatum) Previous() *Datum { return t.prev }

func (t *TextDatum) Calculate() error {
  return CalculateAll(t.data, map[string]CalculateMethod {
    "TextLength": t.CalculateTextLength,
  })
}

func (t *TextDatum) CalculateTextLength() (interface{}, error) {
  return len(t.data["Input"].(string)), nil
}





var DATUM_TYPES map[DatumKind]Datum = map[DatumKind]Datum{
  TEXT: &TextDatum{},
}

var currentDatum *Datum = nil


func Injest(kind DatumKind, input interface{}) {
  currentDatumIndex += 1

  // Make a copy of the empty struct that matches the `kind` of this datum, and set it up for use
  newDatum := DATUM_TYPES[kind]
  newDatum.Build(input, map[string]interface{}{
    "kind": kind,

    "index": currentDatumIndex,
    "next": nil,
    "prev": currentDatum,
  })

  // Link to the next datum from the previous datum
  if currentDatum != nil {
    currentDatum.Next = newDatum
  }

  currentDatum = newDatum
}

func main() {
  Injest(TEXT, "a")
  Injest(TEXT, "b")
  Injest(TEXT, "c")
  Injest(TEXT, "a")
  Injest(TEXT, "b")

  fmt.Println(currentDatum)
  fmt.Println(currentDatum.Prev)
}
