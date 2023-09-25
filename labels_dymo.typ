#{
  set page(width: 3.5in, height: 1.125in, margin: 0em)

  import "common.typ"

  let options = json("options.json")
  let cards = options.cards

  for (idx, card) in cards.enumerate() {
    if idx != 0 {
      pagebreak()
    }
    place(
      top + left,
      dx: 1in/16,
      dy: 1in/16,
      common.address_block(2.5in, 1in, card)
    )
  }
}
