#let address_text(card) = {
  text(font: ("OCR-B", "Noto Emoji"), size: 8pt, card.address)
}

#let place_avatar(text_height, card) = {
  style(styles => {
    let text_offset = (text_height - measure(address_text(card), styles).height) / 2
    place(
      top + left,
      dx: 0.1in,
      dy: calc.max(text_offset + 4pt - 0.15in, 0pt),
      image(card.avatar, width: 0.3in)
    )
  })
}

#let address_content(width, height, card) = {
  set par(leading: 0.5em)
  let text_height = if card.imb == "" {
    height
  } else {
    height - 1in/8
  }

  place(
    top + left,
    dx: 0.5in,
    block(
      width: width - 0.5in,
      height: text_height,
      align(
        start + horizon,
        address_text(card)
      )
    )
  )
  if card.imb != "" {
    place(
      top + left,
      dy: height - 1in/8,
      dx: 0.05in,
      block(
        width: 100%,
        height: 1in/8,
        align(
          top + left,
          text(font: "USPSIMBCompact", size: 12pt, card.imb)
        )
      )
    )
  }
  if card.avatar != none {
    place_avatar(text_height, card)
  }
}

#let address_block(width, height, card) = {
  block(
    width: width,
    height: height,
    breakable: false,
    address_content(width, height, card)
  )
}


#let postcard_content(width, height, content_fn, card) = {
  // Content block
  place(
    top + left,
    dx: 1in/8,
    dy: 1in/8,
    block(
      width: width - 2in - 7in/8,
      height: height - 0.25in,
      breakable: false,
      content_fn(card)
    )
  )

  // Stamp placement guide
  place(
    top + right,
    dx: -0.25in,
    dy: 0.25in,
    image("nixowos.png", width: 0.5in)
  )

  // Address block
  place(
    horizon + right,
    dx: -1in/8,
    address_block(2.5in, 1in, card)
  )
}

#let postcard_block(width, height, content_fn, card) = {
  block(
    width: width,
    height: height,
    breakable: false,
    postcard_content(width, height, content_fn, card)
  )
}

#let postcard_square(width, height, margin, content_fn, card) = {
  rect(
    width: width + margin * 2,
    height: height + margin * 2,
    inset: margin,
    postcard_block(width, height, content_fn, card)
  )
}

#let card_sheets(width, height, margin, args, cards) = {
  let content_fn = if args.no_content {
    _ => []
  } else {
    import "content/content.typ"
    content.content
  }

  for (idx, card) in cards.enumerate() {
    let row = calc.rem(idx + args.skip, 2)
    if idx != 0 and row == 0 {
      pagebreak()
    }

    place(
      top + left,
      dx: 50% - width / 2 - margin,
      dy: 25% - height / 2 - margin + 50% * row,
      postcard_square(width, height, margin, content_fn, card)
    )
  }
}
