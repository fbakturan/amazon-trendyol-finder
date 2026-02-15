import streamlit as st
import pandas as pd
from scraper import scrape_all_categories, filter_brands
import time

APIFY_API_TOKEN = "apify_api_VCb1D6HbNGS4IfU1OC4e5asnqgHe3U1CLkg8"
GEMINI_API_KEY = "AIzaSyBKZB4HEGIRbhSqXK6aRwRZwu3uddCOLL4"

st.set_page_config(page_title="Amazon → Trendyol Fırsat Bulucu", page_icon="🎯", layout="wide")
st.title("🎯 Amazon Movers & Shakers → Fırsat Ürün Bulucu")
st.markdown("**9 kategoriden** büyük markaları filtreleyerek **fırsat ürünleri** bulur.")

st.sidebar.header("⚙️ Ayarlar")
st.sidebar.success("✅ API Keys yüklü!")

st.sidebar.subheader("📂 Kategoriler")
all_categories = ["Electronics", "Home & Kitchen", "Tools & Home Improvement", "Automotive", "Cell Phones & Accessories", "Computers & Accessories", "Kitchen & Dining", "Pet Supplies", "Sports & Outdoors"]

selected_categories = []
for cat in all_categories:
    if st.sidebar.checkbox(cat, value=True):
        selected_categories.append(cat)

max_items = st.sidebar.slider("Kategori başına max ürün:", 10, 100, 100)

col1, col2, col3 = st.columns(3)
metric1 = col1.empty()
metric2 = col2.empty()
metric3 = col3.empty()

metric1.metric("📦 Toplam Taranan", "-")
metric2.metric("🚫 Büyük Marka Elenen", "-")
metric3.metric("🎯 Fırsat Ürünler", "-")

if st.button("🚀 TARAMAYI BAŞLAT", type="primary", use_container_width=True):
    if not selected_categories:
        st.error("❌ En az bir kategori seçin!")
        st.stop()
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    all_results = []
    total_scraped = 0
    total_filtered = 0
    
    for idx, category in enumerate(selected_categories):
        status_text.info(f"🔍 **{category}** taranıyor... ({idx+1}/{len(selected_categories)})")
        try:
            products = scrape_all_categories(APIFY_API_TOKEN, [category], max_items_per_category=max_items)
            if products:
                filtered = filter_brands(products, category)
                scraped_count = len(products)
                filtered_count = len(filtered)
                total_scraped += scraped_count
                total_filtered += (scraped_count - filtered_count)
                all_results.extend(filtered)
                status_text.success(f"✅ {category}: {scraped_count} taranan → {filtered_count} fırsat")
        except Exception as e:
            status_text.error(f"❌ {category} hatası: {e}")
        progress_bar.progress((idx + 1) / len(selected_categories))
        time.sleep(1)
    
    progress_bar.progress(100)
    status_text.success("✅ **Tarama tamamlandı!**")
    metric1.metric("📦 Toplam Taranan", total_scraped)
    metric2.metric("🚫 Büyük Marka Elenen", total_filtered)
    metric3.metric("🎯 Fırsat Ürünler", len(all_results))
    
    if all_results:
        st.balloons()
        st.success(f"🎉 **{len(all_results)} FIRSAT ÜRÜN BULUNDU!**")
        df = pd.DataFrame(all_results)
        col_filter1, col_filter2 = st.columns(2)
        with col_filter1:
            category_filter = st.multiselect("Kategori Filtresi:", df['category'].unique(), default=df['category'].unique())
        with col_filter2:
            price_range = st.slider("Fiyat Aralığı ($):", 0, 500, (0, 500))
        filtered_df = df[(df['category'].isin(category_filter)) & (df['price'] >= price_range[0]) & (df['price'] <= price_range[1])]
        st.dataframe(filtered_df[['title', 'brand', 'price', 'category', 'amazon_url', 'rating']], use_container_width=True, hide_index=True, column_config={"amazon_url": st.column_config.LinkColumn("Amazon Link"), "price": st.column_config.NumberColumn("Price ($)", format="$%.2f"), "rating": st.column_config.NumberColumn("Rating", format="⭐ %.1f")})
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 TÜM SONUÇLARI CSV OLARAK İNDİR", csv, "amazon_firsat_urunler.csv", "text/csv", use_container_width=True)
        st.markdown("---")
        st.subheader("📊 İstatistikler")
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("Ortalama Fiyat", f"${df['price'].mean():.2f}")
        with col_stat2:
            st.metric("En Ucuz", f"${df['price'].min():.2f}")
        with col_stat3:
            st.metric("En Pahalı", f"${df['price'].max():.2f}")
    else:
        st.warning("⚠️ Hiç fırsat ürün bulunamadı. Farklı kategoriler deneyin!")

st.markdown("---")
st.caption("🚀 Made with Streamlit + Apify | Amazon Movers & Shakers Analyzer")
