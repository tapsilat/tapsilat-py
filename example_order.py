import os
import json
import uuid
from tapsilat_py.client import TapsilatAPI
from tapsilat_py.models import (
    OrderCreateDTO,
    BuyerDTO,
    BasketItemDTO,
    CancelOrderDTO,
    OrderConsent,
    AddBasketItemRequest,
)


def load_env(env_path):
    try:
        from dotenv import load_dotenv

        load_dotenv(dotenv_path=env_path)
    except ImportError:
        try:
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ[k.strip()] = v.strip().strip("'").strip('"')
        except FileNotFoundError:
            pass


def print_step(title, desc=""):
    print("\n" + "=" * 60)
    print(f"👉 SONRAKİ ADIM: {title}")
    if desc:
        print(f"Açıklama: {desc}")
    print("=" * 60)
    input("=> Onaylamak ve işleme devam etmek için ENTER'a basın...\n")


def pretty_print(data):
    try:
        if isinstance(data, dict):
            print(json.dumps(data, indent=4, ensure_ascii=False))
        elif hasattr(data, "__dict__"):
            print(json.dumps(data.__dict__, indent=4, ensure_ascii=False))
        else:
            print(data)
    except TypeError:
        print(data)


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(base_dir, ".env")

    # 1. Load API key from .env file
    load_env(env_path)

    api_key = os.environ.get("TAPSILAT_API_KEY")
    if not api_key:
        print(
            f"HATA: API_KEY bulunamadı! Lütfen '{env_path}' dosyasını kontrol edin ve içerikte 'TAPSILAT_API_KEY' tanımlı olduğundan emin olun."
        )
        return

    client = TapsilatAPI(api_key=api_key)

    # --- ADIM 1: SİPARİŞ OLUŞTURMA ---
    print_step(
        "Sipariş Oluştur (create_order)",
        "API üzerinden mock veriyle yeni bir örnek sipariş oluşturulacak.",
    )

    order_req = OrderCreateDTO(
        amount=150.75,
        currency="TRY",
        locale="tr",
        buyer=BuyerDTO(
            name="Can",
            surname="Deneme",
            gsm_number="+905554443322",
            city="Ankara",
            country="Türkiye",
            email="can.deneme@example.com",
            id="BYR-9999",
            identity_number="11111111111",
            ip="85.15.25.35",
            registration_date="2022-01-01 10:00:00",
            last_login_date="2023-10-01 10:00:00",
        ),
        basket_items=[
            BasketItemDTO(
                id="ITEM-101",
                name="Premium Üyelik (Test)",
                item_type="VIRTUAL",
                price=150.75,
                category1="Abonelik",
                category2="Dijital",
            )
        ],
        consents=[
            OrderConsent(
                title="Mesafeli Satış Sözleşmesi", url="https://example.com/mss"
            )
        ],
        conversation_id=f"CONV-DEMO-{uuid.uuid4().hex[:8]}",
    )

    print("İstek gönderiliyor...")
    try:
        response = client.create_order(order_req)
        print("\n✅ Sipariş başarıyla oluşturuldu!")
        print("Gelen Yanıt (Response):")
        pretty_print(response)

        reference_id = getattr(
            response, "reference_id", response.get("reference_id", None)
        )

        try:
            checkout_url = client.get_checkout_url(reference_id)
        except Exception:
            checkout_url = None

        if checkout_url:
            print("\n" + "*" * 60)
            print("💳 ÖDEME LİNKİ:")
            print(checkout_url)
            print(
                "Lütfen bu linke tıklayarak (veya tarayıcıya kopyalayarak) ödeme işlemini gerçekleştirin."
            )
            print(
                "Ödeme tamamlandıktan sonra terminale dönerek işleme devam edebilirsiniz."
            )
            print("*" * 60 + "\n")
        else:
            print("⚠️ Checkout URL dönmedi.")
            return

    except Exception as e:
        print(f"❌ Sipariş oluşturulurken hata: {e}")
        return

    # --- ADIM 1.5: SEPETE YENİ ÜRÜN EKLEME ---
    print_step(
        "Sepete Ürün Ekle (add_basket_item)",
        f"Oluşturulan siparişe ({reference_id}) yeni bir kalem eklenecek.",
    )
    try:
        basket_req = AddBasketItemRequest(
            order_reference_id=reference_id,
            basket_item=BasketItemDTO(
                id="ITEM-102",
                name="Ek Hizmet Bedeli",
                item_type="VIRTUAL",
                price=20.00,
                category1="Hizmet",
                category2="Ekstra",
            ),
        )
        basket_res = client.add_basket_item(basket_req)
        print("\n✅ Sepete ürün eklendi!")
        pretty_print(basket_res)
    except Exception as e:
        print(f"❌ Sepete ürün eklenirken hata: {e}")

    # --- ADIM 2: SİPARİŞ DURUMU ALMA ---
    print_step(
        "Sipariş Durumu Getir (get_order_status)",
        f"Mevcut siparişin ({reference_id}) güncel durumu API'den sorgulanacak.",
    )
    try:
        status_res = client.get_order_status(reference_id)
        print("\n✅ Durum Yanıtı:")
        pretty_print(status_res)
    except Exception as e:
        print(f"❌ Sipariş durumu alınırken hata: {e}")

    # --- ADIM 3: SİPARİŞ DETAYLARI ALMA ---
    print_step(
        "Sipariş Detaylarını Getir (get_order)",
        f"Sipariş ({reference_id}) hakkında tüm detaylı veri API'den çekilecek.",
    )
    try:
        order_details = client.get_order(reference_id)
        print("\n✅ Sipariş Detay Yanıtı:")
        pretty_print(order_details)
    except Exception as e:
        print(f"❌ Sipariş detayları alınırken hata: {e}")

    # --- ADIM 4: SİPARİŞ ÖDEME DETAYLARI ALMA ---
    print_step(
        "Sipariş Ödeme Detaylarını Getir (get_order_payment_details_by_id)",
        "Ödeme yapıldıysa provizyon vb. ödeme detayları alınacak.",
    )
    try:
        payment_details = client.get_order_payment_details_by_id(reference_id)
        print("\n✅ Sipariş Ödeme Detayları Yanıtı:")
        pretty_print(payment_details)
    except Exception as e:
        print(f"❌ Ödeme detayları alınırken hata (veya henüz ödeme yapılmadı): {e}")

    # --- ADIM 5: SİPARİŞ İPTALİ ---
    print_step(
        "Siparişi İptal Et / Sil (cancel_order)",
        f"Eğer ödeme yaptıysanız/yapmadıysanız tüm işlemler bittiğinde sipariş ({reference_id}) sistemden iptal edilecek.",
    )
    try:
        cancel_req = CancelOrderDTO(reference_id=reference_id)
        cancel_res = client.cancel_order(cancel_req)
        print("\n✅ Sipariş İptal Yanıtı:")
        pretty_print(cancel_res)
    except Exception as e:
        print(f"❌ İptal sırasında hata oluştu: {e}")

    print("\n🎉 Tüm örnek sipariş akışı başarıyla tamamlandı!")


if __name__ == "__main__":
    main()
