from config import TARGET_SITES

from scrapers.scraper_static import scrape_multiple as scrape_static, crawl_site
from scrapers.scraper_dynamic import scrape_dynamic_multiple

from database.mongo_connector import save_page
from database.elastic_connector import index_page

from graph_mining.pagerank_hits import compute_metrics
from graph_mining.community_detection import detect_link_farms

from usage_mining.bot_detector import simulate_logs, detect_bots


def main():
    print("=" * 50)
    print("   CYBERINTEL — Pipeline Personne A")
    print("=" * 50)

    #  PHASE 1 : Scraping
  
    print("\n[1/4] Scraping des sites cibles...")

    
    static_sites = TARGET_SITES[:7]
    dynamic_sites = TARGET_SITES[7:]

  
    # STATIC SCRAPING
   
    print("\n[STATIC SCRAPING]")
    static_pages = scrape_static(static_sites)

    # DYNAMIC SCRAPING

    print("\n[DYNAMIC SCRAPING]")
    dynamic_pages = scrape_dynamic_multiple(dynamic_sites)

   
    # CRAWLING
  
    print("\n[CRAWLING EXTENDED DATA]")
    crawled_pages = []

    for site in TARGET_SITES:
        try:
            pages = crawl_site(site, max_pages=30)  
            crawled_pages.extend(pages)
        except Exception as e:
            print(f"[CRAWL ERROR] {site}: {e}")

    # Combine all
    pages = static_pages + dynamic_pages + crawled_pages

    print(f"\n[INFO] Total pages collectees: {len(pages)}")

    #  Save data
 
    saved_count = 0

    for page in pages:
        try:
            save_page(page)
            index_page(page)
            saved_count += 1
        except Exception:
            continue

    print(f"\n  {saved_count} pages sauvegardees")

    #  PHASE 2 : Graph Mining
  
    print("\n[2/4] Analyse du graphe de liens...")
    compute_metrics()
=
    #  PHASE 3 : Link Farms
   
    print("\n[3/4] Detection des communautes suspectes...")
    detect_link_farms()

  
    #  PHASE 4 : Bots
  
    print("\n[4/4] Analyse comportementale...")

    if pages:
        logs = simulate_logs(pages)
        detect_bots(logs)
    else:
        print("[WARNING] Pas de donnees pour analyser les bots")

    print("\n[DONE] Pipeline termine avec succes !")


if __name__ == "__main__":
    main()