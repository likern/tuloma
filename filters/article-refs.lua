-- Number article equations, figures and tables and resolve grammatical links.
-- Uses native Pandoc nodes so MathML and the standalone Pandoc build agree.
function Pandoc(doc)
  local references = {}
  local counts = {equation=0, figure=0, table=0}
  doc = doc:walk({Para = function(para)
    if #para.content == 1 and para.content[1].tag == "Math"
       and para.content[1].mathtype == "DisplayMath" then
      return pandoc.Div({para}, pandoc.Attr("", {"math-display"}))
    end
  end, Div = function(div)
    if div.classes:includes("algorithm") then
      references[div.identifier] = {number=div.attributes["data-algorithm-number"], kind="algorithm"}
      return div
    end
    local kind
    if div.classes:includes("equation") then kind="equation"
    elseif div.classes:includes("numbered-figure") then kind="figure"
    elseif div.classes:includes("numbered-table") then kind="table" end
    if not kind then return nil end
    if div.identifier == "" then error("Нумерованный объект требует идентификатора.") end
    counts[kind] = counts[kind] + 1
    local number = counts[kind]
    references[div.identifier] = {number=number, kind=kind}
    if kind == "equation" then
      div.content:insert(pandoc.Plain({pandoc.Span({pandoc.Str("("..number..")")}, pandoc.Attr("", {"eqno"}))}))
    else
      local prefix = kind == "figure" and "Рисунок " or "Таблица "
      local caption = pandoc.List({pandoc.Strong({pandoc.Str(prefix..number..".")}),pandoc.Space()})
      local text = pandoc.read(div.attributes.caption or "", "markdown").blocks[1]
      if text and text.content then caption:extend(text.content) end
      local captionBlock = pandoc.Div({pandoc.Plain(caption)}, pandoc.Attr(div.identifier.."-caption", {"object-caption"}))
      if kind == "figure" then div.content:insert(captionBlock)
      else div.content:insert(1, captionBlock) end
      div.attributes["aria-labelledby"] = div.identifier.."-caption"
      if kind == "figure" then div.attributes.role = "figure" end
      div.attributes.caption = nil
    end
    return div
  end})
  return doc:walk({Link = function(link)
    if not link.classes:includes("xref") then return nil end
    local target = references[link.target:sub(2)]
    if not target then error("Не найдена перекрёстная ссылка: "..link.target) end
    link.content:insert(pandoc.Space())
    link.content:insert(pandoc.Str(target.kind == "equation" and "("..target.number..")" or tostring(target.number)))
    return link
  end})
end
