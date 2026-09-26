-- A figure written `![](_images/name)` has no caption: the drawing's
-- own title and labels say what it shows. build_site.rewrite_images()
-- and build_epub.rewrite_images() give its image the SVG's <title> as
-- alt text, which makes pandoc build a figure, and the class
-- `nocaption`; this filter then drops the caption pandoc copies from
-- that alt text, so the figure keeps its layout and its alt text but
-- prints no caption. Typst prints "Figure N:" before even an empty
-- caption, so there the figure becomes its image, centered; pandoc
-- still resolves and embeds the image as it does inside a figure.
local function marked_image(fig)
  local found = nil
  fig:walk({
    Image = function(img)
      if img.classes:includes("nocaption") then found = img end
    end,
  })
  return found
end

function Figure(fig)
  local img = marked_image(fig)
  if img == nil then
    return nil
  end
  if FORMAT:match("typst") then
    return {
      pandoc.RawBlock("typst", "#align(center)["),
      pandoc.Para({img}),
      pandoc.RawBlock("typst", "]"),
    }
  end
  fig.caption.long = {}
  fig.caption.short = nil
  return fig
end
