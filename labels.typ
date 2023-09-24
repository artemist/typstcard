#{
  set page("us-letter", margin: 0em)

  import "common.typ"
 
  let options = json("options.json")
  let cards = options.cards
  let args = options.args

  let printer_offset = 1in/16
  
  let label_position(idx) = {
    let offset_idx = idx + args.skip
    let col = calc.rem(offset_idx, 3)
    let row = calc.rem(calc.floor(offset_idx / 3), 10)
    let x_pos = 3in/16 + 2.75in * col
    let y_pos = printer_offset + 1in/2 + 1in * row
    (x_pos, y_pos)
  }


  for (idx, card) in cards.enumerate() {
    if idx != 0 and calc.rem(idx + args.skip, 30) == 0 {
      pagebreak()
    }
    let (dx, dy) = label_position(idx)
    place(
      top + left,
      dx: dx,
      dy: dy,
      common.address_block(2in + 5in/8, 7in/8, card)
    )
  }
}
