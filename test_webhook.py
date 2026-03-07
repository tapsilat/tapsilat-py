from fastapi import FastAPI, Request, Header, HTTPException
import uvicorn
import os
import json
from tapsilat_py.client import TapsilatAPI

app = FastAPI(title="Tapsilat Webhook Test Sunucusu")

# Eğer webhook_secret .env dosyasından gelmiyorsa buraya yazabilirsiniz
WEBHOOK_SECRET = os.environ.get(
    "TAPSILAT_WEBHOOK_SECRET", "sizin_gizli_webhook_anahtariniz_degisecek"
)


@app.post("/webhook/success")
async def handle_success_webhook(
    request: Request, x_signature: str = Header(None, alias="X-Signature")
):
    """
    Tapsilat'tan başarılı ödemeler vb. geldiğinde tetiklenecek endpoint.
    Not: Tapsilat gercek webhook isteklerinde x-signature gonderir.
    Eğer test ediyorsanız bu isim değişebilir, o yüzen x-signature yerine gelen tüm headerları da kontrol etmekte fayda var.
    """
    raw_body = await request.body()
    body_str = raw_body.decode("utf-8")

    print("\n" + "=" * 50)
    print("🔔 YENİ BİR WEBHOOK İSTEĞİ GELDİ! (SUCCESS)")
    print(f"Gelen İmza (Signature): {x_signature}")

    # Tüm Headerları Yazdır (Debug için)
    print("\n[HEADERS]")
    for key, value in request.headers.items():
        print(f"{key}: {value}")

    print("\n[PAYLOAD/GÖVDE]")
    try:
        data = json.loads(body_str)
        print(json.dumps(data, indent=4, ensure_ascii=False))
    except json.JSONDecodeError:
        print(body_str)

    # İmza doğrulama adımı (Eğer Tapsilat imzayı x-signature veya benzeri yolluyorsa)
    if x_signature and WEBHOOK_SECRET != "sizin_gizli_webhook_anahtariniz_degisecek":
        # Signature formatını tapsilat_py verify_webhook için de uygunsa kullanın
        # (Genelde "sha256=..." formatında gönderir). Gelen formata göre düzenleyebilirsiniz.
        is_valid = TapsilatAPI.verify_webhook(body_str, x_signature, WEBHOOK_SECRET)
        if is_valid:
            print("\n✅ İmza Doğrulandı! (Güvenilir Kaynak)")
        else:
            print("\n❌ İmza Doğrulaması Başarısız! (Güvenilmeyen Kaynak)")
    else:
        print(
            "\n⚠️ İmza kontrolü atlandı (x-signature eksik veya secret tanımlanmamış)."
        )

    print("=" * 50 + "\n")

    # Tapsilat genelde 200 HTTP kodu bekler, yoksa yeniden deneme yapabilir.
    return {"status": "ok", "message": "Webhook başarıyla alındı"}


@app.post("/webhook/{event_type}")
async def handle_generic_webhook(
    event_type: str,
    request: Request,
):
    """
    Fail, refund, cancel vb. diğer işlemleri karşılamak için
    """
    raw_body = await request.body()
    body_str = raw_body.decode("utf-8")

    print("\n" + "*" * 50)
    print(f"🔔 YENİ BİR WEBHOOK İSTEĞİ GELDİ! ({event_type.upper()})")

    # Tüm Headerlar
    print("\n[HEADERS]")
    for key, value in request.headers.items():
        print(f"{key}: {value}")

    print("\n[PAYLOAD/GÖVDE]")
    try:
        data = json.loads(body_str)
        print(json.dumps(data, indent=4, ensure_ascii=False))
    except json.JSONDecodeError:
        print(body_str)

    print("*" * 50 + "\n")

    return {"status": "ok"}


if __name__ == "__main__":
    print("🚀 Tapsilat Webhook Dinleyici Başlatılıyor...")
    print("👉 Sunucu: http://0.0.0.0:8000")
    print("Cloudflare veya ngrok ile dışarıya açtığınızda URL örneği:")
    print(" - https://api.grow.tr/webhook/success")
    print(" - https://api.grow.tr/webhook/fail")
    print(
        "\nLütfen .env dosyanızda TAPSILAT_WEBHOOK_SECRET anahtarınızı (varsa) tanımlamayı unutmayın!\n"
    )
    uvicorn.run(app, host="0.0.0.0", port=8000)
