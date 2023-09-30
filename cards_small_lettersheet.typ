#{
  set page("us-letter", margin: 0em)

  import "common.typ"

  let options = json("options.json")
  let cards = options.cards
  let args = options.args

  common.card_sheets(149mm, 99mm, 1in/16, args, cards)

}
