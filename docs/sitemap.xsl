---
layout: null
permalink: /sitemap.xsl
---
<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
  xmlns:html="http://www.w3.org/TR/REC-html40"
  xmlns:sitemap="http://www.sitemaps.org/schemas/sitemap/0.9"
  xmlns:xhtml="http://www.w3.org/1999/xhtml"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
        <title>PyOrchestrator Sitemap</title>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
        <style type="text/css">
          body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #e2e8f0; background: #09090b; margin: 0; padding: 2rem; }
          h1 { font-size: 1.5rem; margin: 0 0 0.5rem; }
          p { color: #94a3b8; margin: 0 0 1.5rem; }
          table { border-collapse: collapse; width: 100%; max-width: 1100px; }
          th, td { text-align: left; padding: 0.65rem 0.75rem; border-bottom: 1px solid #27272a; font-size: 0.9rem; }
          th { color: #94a3b8; font-weight: 600; }
          a { color: #22d3ee; text-decoration: none; }
          a:hover { text-decoration: underline; }
          .muted { color: #64748b; }
        </style>
      </head>
      <body>
        <h1>PyOrchestrator Sitemap</h1>
        <p>XML sitemap for search engines (<xsl:value-of select="count(sitemap:urlset/sitemap:url)"/> URLs).</p>
        <table>
          <tr>
            <th>URL</th>
            <th>Last modified</th>
            <th>Change frequency</th>
            <th>Priority</th>
          </tr>
          <xsl:for-each select="sitemap:urlset/sitemap:url">
            <tr>
              <td><a href="{sitemap:loc}"><xsl:value-of select="sitemap:loc"/></a></td>
              <td class="muted"><xsl:value-of select="sitemap:lastmod"/></td>
              <td class="muted"><xsl:value-of select="sitemap:changefreq"/></td>
              <td class="muted"><xsl:value-of select="sitemap:priority"/></td>
            </tr>
          </xsl:for-each>
        </table>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
