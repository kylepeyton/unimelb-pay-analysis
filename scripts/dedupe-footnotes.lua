-- Pandoc expands repeated Markdown footnote references into separate Note nodes.
-- Retain the first note and point subsequent HTML citations to its existing number.
function Pandoc(doc)
  if not FORMAT:match('html') then return doc end
  local numbers = {}
  local count = 0
  return doc:walk({
    Note = function(note)
      local key = pandoc.write(pandoc.Pandoc(note.content), 'native')
      local number = numbers[key]
      if number then
        return pandoc.RawInline('html', string.format(
          '<a href="#fn%d" class="footnote-ref" role="doc-noteref" aria-label="Footnote %d"><sup>%d</sup></a>',
          number, number, number))
      end
      count = count + 1
      numbers[key] = count
      return note
    end
  })
end
