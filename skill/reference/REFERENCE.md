# Confluence Automation Reference

## HTML Macros

```html
<!-- TOC — never wrap in <p> tags, renders as a stray dot -->
<ac:structured-macro ac:name="toc">
  <ac:parameter ac:name="maxLevel">3</ac:parameter>
</ac:structured-macro>

<!-- Info Panel -->
<ac:structured-macro ac:name="info">
  <ac:rich-text-body><p>Text</p></ac:rich-text-body>
</ac:structured-macro>

<!-- Code Block -->
<ac:structured-macro ac:name="code">
  <ac:parameter ac:name="language">python</ac:parameter>
  <ac:plain-text-body><![CDATA[code here]]></ac:plain-text-body>
</ac:structured-macro>

<!-- Warning -->
<ac:structured-macro ac:name="warning">
  <ac:rich-text-body><p>Warning</p></ac:rich-text-body>
</ac:structured-macro>
```

Script auto-escapes special characters.

## Diagrams

Ask user to convert .drawio to PNG, then attach:
```bash
python src/attach_image.py PAGE_ID diagram.png "Description"
```

Always center diagrams — wrap every `ac:image` in a centered div:
```html
<div style="text-align: center;">
  <ac:image ac:width="800">
    <ri:attachment ri:filename="diagram.png"/>
  </ac:image>
</div>
```
