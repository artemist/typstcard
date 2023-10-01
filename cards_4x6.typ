#{
  set page(width: 6in, height: 4in, margin: 0em)

  import "common.typ"

  let options = json("options.json")
  let cards = options.cards
  let args = options.args

  let content_fn = if args.no_content {
    _ => []
  } else {
    import "content/content.typ"
    content.content
  }

  for (idx, card) in cards.enumerate() {
    if idx != 0 {
      pagebreak()
    }
    common.postcard_content(100%, 100%, content_fn, card)
  }
}
