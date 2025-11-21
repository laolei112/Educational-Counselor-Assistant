from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from backend.models.tb_primary_schools import TbPrimarySchools
from backend.models.tb_secondary_schools import TbSecondarySchools
from django.utils import timezone

# Cache for 1 hour (3600 seconds)
# Sitemaps don't change that often, so caching is good.
@cache_page(60 * 60)
def sitemap_view(request):
    """
    Generate dynamic sitemap.xml for SEO
    """
    # Base URL
    base_url = "https://betterschool.hk"
    
    # XML Header
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    # Static Pages
    static_pages = [
        '/',
        '/primary',
        '/secondary',
    ]
    
    now = timezone.now().strftime('%Y-%m-%d')
    
    # Add static pages
    for path in static_pages:
        xml.append('  <url>')
        xml.append(f'    <loc>{base_url}{path}</loc>')
        xml.append('    <changefreq>daily</changefreq>')
        xml.append('    <priority>1.0</priority>')
        xml.append(f'    <lastmod>{now}</lastmod>')
        xml.append('  </url>')

    # Dynamic Pages - Primary Schools
    # Only select ID and updated_at to be efficient
    primary_schools = TbPrimarySchools.objects.all().only('id', 'updated_at')
    for school in primary_schools:
        # Format: /school/primary/:id
        url = f"{base_url}/school/primary/{school.id}"
        last_mod = school.updated_at.strftime('%Y-%m-%d') if school.updated_at else now
        
        xml.append('  <url>')
        xml.append(f'    <loc>{url}</loc>')
        xml.append('    <changefreq>weekly</changefreq>')
        xml.append('    <priority>0.8</priority>')
        xml.append(f'    <lastmod>{last_mod}</lastmod>')
        xml.append('  </url>')
        
    # Dynamic Pages - Secondary Schools
    secondary_schools = TbSecondarySchools.objects.all().only('id', 'updated_at')
    for school in secondary_schools:
        # Format: /school/secondary/:id
        url = f"{base_url}/school/secondary/{school.id}"
        last_mod = school.updated_at.strftime('%Y-%m-%d') if school.updated_at else now
        
        xml.append('  <url>')
        xml.append(f'    <loc>{url}</loc>')
        xml.append('    <changefreq>weekly</changefreq>')
        xml.append('    <priority>0.8</priority>')
        xml.append(f'    <lastmod>{last_mod}</lastmod>')
        xml.append('  </url>')

    xml.append('</urlset>')
    
    return HttpResponse('\n'.join(xml), content_type="application/xml")

