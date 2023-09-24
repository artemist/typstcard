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
      block(
        width: 100%,
        height: 1in/8,
        align(
          top + center,
          text(font: "USPSIMBCompact", size: 12pt, card.imb)
        )
      )
    )
  }
  if card.avatar != "" {
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
