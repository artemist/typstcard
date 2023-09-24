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
      fill: luma(230),
      align(
        start + horizon,
        text(font: ("OCR-B", "Noto Emoji"), size: 8pt, card.address)
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
        fill: luma(220),
        align(
          top + center,
          text(font: "USPSIMBCompact", size: 12pt, card.imb)
        )
      )
    )
  }
  if card.avatar != "" {
    place(
      top + left,
      dx: 0.1in,
      dy: 0.1in,
      image(card.avatar, width: 0.3in)
    )
  }
}

#let address_block(width, height, card) = {
  block(
    width: width,
    height: height,
    breakable: false,
    fill: luma(240),
    address_content(width, height, card)
  )
}
