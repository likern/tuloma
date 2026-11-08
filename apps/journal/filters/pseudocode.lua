-- Typeset indented pseudocode using Pandoc's own inline mathematics.
-- No browser runtime or second mathematics renderer is needed.
local algorithm_number = 0
local keywords = {
  "Иначе если", "Для каждого", "Вход", "Выход", "Вернуть", "Если", "Иначе",
  "Пока", "Для", "Прервать", "Продолжить",
  "Input", "Output", "Require", "Ensure", "else if", "for each", "return",
  "while", "break", "continue", "if", "else", "for",
}

local function attr(id, classes, attributes)
  return pandoc.Attr(id or "", classes or {}, attributes or {})
end

local function inlines(text)
  local parsed = pandoc.read(text, "markdown+tex_math_dollars-smart")
  if #parsed.blocks ~= 1 or not parsed.blocks[1].content then
    error("Псевдокод: каждая строка должна содержать один абзац.")
  end
  return parsed.blocks[1].content
end

local function statement(text)
  if text:sub(1, 2) == "//" then
    return pandoc.Span(inlines(text), attr("", {"algorithm-comment"}))
  end
  for _, keyword in ipairs(keywords) do
    local rest = text:sub(#keyword + 1)
    if text:sub(1, #keyword) == keyword
        and (rest == "" or rest:match("^[%s:]")) then
      if rest:sub(1, 1) == ":" then
        keyword, rest = keyword .. ":", rest:sub(2)
      end
      local content = pandoc.List({pandoc.Strong({pandoc.Str(keyword)})})
      if rest ~= "" then
        content:insert(pandoc.Space())
        content:extend(inlines(rest:gsub("^%s+", "")))
      end
      return pandoc.Span(content)
    end
  end
  return pandoc.Span(inlines(text))
end

function CodeBlock(block)
  if not block.classes:includes("pseudocode") then return nil end
  local width = tonumber(block.attributes.indent or "2")
  if not width or width < 1 or width % 1 ~= 0 then
    error("Псевдокод: indent должен быть положительным целым числом.")
  end
  local rows = {}
  for raw in (block.text .. "\n"):gmatch("([^\n]*)\n") do
    raw = raw:gsub("\r$", "")
    if raw:find("\t") then error("Псевдокод: используйте пробелы вместо табуляции.") end
    if raw:match("%S") then
      local spaces, text = raw:match("^( *)(.*)$")
      if #spaces % width ~= 0 then
        error("Псевдокод: отступ строки должен быть кратен indent.")
      end
      local depth = #spaces / width
      local previous = rows[#rows]
      if (not previous and depth ~= 0) or (previous and depth > previous.depth + 1) then
        error("Псевдокод: вложенность должна увеличиваться на один уровень.")
      end
      rows[#rows + 1] = {depth = depth, text = text}
    end
  end
  if #rows == 0 then error("Псевдокод: блок не должен быть пустым.") end

  algorithm_number = algorithm_number + 1
  local id = block.identifier ~= "" and block.identifier or ("algorithm-" .. algorithm_number)
  local caption_id = id .. "-caption"
  local caption = pandoc.List({
    pandoc.Strong({pandoc.Str("Алгоритм " .. algorithm_number)}),
    pandoc.Space(), pandoc.Str("·"), pandoc.Space(),
  })
  caption:extend(inlines(block.attributes.caption or "Псевдокод"))
  local permalink = pandoc.Link({pandoc.Str("§")}, "#" .. id, "", attr("", {"algorithm-permalink"}, {
    ["aria-label"] = "Ссылка на алгоритм " .. algorithm_number,
  }))
  caption:insert(pandoc.Space())
  caption:insert(permalink)

  local lines = pandoc.List()
  for index, row in ipairs(rows) do
    local line_id = id .. "-L" .. index
    local body = pandoc.List()
    for level = 1, row.depth do
      local classes = {"algorithm-guide"}
      if index == #rows or rows[index + 1].depth < level then
        classes[#classes + 1] = "algorithm-guide-end"
      end
      body:insert(pandoc.Span({}, attr("", classes, {
        style = "--level: " .. level, ["aria-hidden"] = "true",
      })))
    end
    body:insert(statement(row.text))
    lines:insert(pandoc.Div({
      pandoc.Plain({pandoc.Link({pandoc.Str(tostring(index))}, "#" .. line_id, "",
        attr("", {"algorithm-line-number"}, {["aria-label"] = "Строка " .. index}))}),
      pandoc.Div({pandoc.Plain(body)}, attr("", {"algorithm-statement"}, {
        style = "--depth: " .. row.depth,
      })),
    }, attr(line_id, {"algorithm-line"})))
  end
  return pandoc.Div({
    pandoc.Div({pandoc.Plain(caption)}, attr(caption_id, {"algorithm-caption"})),
    pandoc.Div(lines, attr("", {"algorithm-lines"})),
  }, attr(id, {"algorithm"}, {
    role = "figure", ["aria-labelledby"] = caption_id,
    ["data-algorithm-number"] = tostring(algorithm_number),
  }))
end
