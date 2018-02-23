package main

import (
  "fmt"
)

type DatumKind string

const (
  TEXT DatumKind = "TEXT"
  IMAGE = "IMAGE"
  VIDEO_FRAME = "VIDEO_FRAME"
)

var currentDatumIndex int = 0
type Datum struct {
  Kind DatumKind

  Index int
  Next *Datum
  Prev *Datum

  Data map[string]interface{}
}

func (d *Datum) LinkNext(n *Datum) {
  d.Next = n
}


var currentDatum *Datum = nil


func Injest(kind DatumKind, input interface{}) {
  currentDatumIndex += 1
  newDatum := &Datum{
    Kind: kind,

    Index: currentDatumIndex,
    Next: nil,
    Prev: currentDatum,

    Data: map[string]interface{}{
      "Input": input,
    },
  }

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
