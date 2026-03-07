import os
import json
import uuid
import time

from tapsilat_py.client import TapsilatAPI
from tapsilat_py.models import (
    SubscriptionCreateRequest,
    SubscriptionUser,
    SubscriptionBilling,
    SubscriptionGetRequest,
    SubscriptionCancelRequest,
    SubscriptionRedirectRequest,
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


def get_future_timestamp(days=1):
    return int(time.time()) + (days * 86400)


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(base_dir, ".env")

    load_env(env_path)
    api_key = os.environ.get("TAPSILAT_API_KEY")
    if not api_key:
        print(f"HATA: API_KEY bulunamadı! '{env_path}' dosyasını kontrol edin.")
        return

    client = TapsilatAPI(api_key=api_key)

    # --- ADIM 1: ABONELİK OLUŞTURMA ---
    print_step(
        "Abonelik Oluştur (create_subscription)",
        "API üzerinden mock veriyle yeni bir örnek abonelik oluşturulacak.",
    )

    mac_guid = uuid.uuid4().hex[:8]
    sub_req = SubscriptionCreateRequest(
        amount=99.99,
        title=f"Aylık Premium Üyelik ({mac_guid})",
        currency="TRY",
        cycle=1,  # Her tahsilatta 1 dönemi kapsar
        period=1,  # 1 Ay
        external_reference_id=f"EXT-SUB-{mac_guid}",
        payment_date=get_future_timestamp(1),  # Yarıne ait epoch süresi (opsiyonel)
        success_url="https://example.com/success",
        failure_url="https://example.com/failure",
        user=SubscriptionUser(
            id=f"USR-{mac_guid}",
            first_name="Can",
            last_name="Deneme",
            phone="+905554443322",
            email="can.deneme@example.com",
            identity_number="11111111111",
            city="İstanbul",
            country="Türkiye",
            address="Örnek Mah. Örnek Sok. No:1",
            zip_code="34000",
        ),
        billing=SubscriptionBilling(
            contact_name="Can Deneme",
            city="İstanbul",
            country="Türkiye",
            address="Örnek Mah. Örnek Sok. No:1",
            zip_code="34000",
        ),
    )

    print("İstek gönderiliyor...")
    try:
        response = client.create_subscription(sub_req)
        print("\n✅ Abonelik başarıyla oluşturuldu!")
        print("Gelen Yanıt (Response):")
        pretty_print(response)

        # Abone referans numarasını saklama
        reference_id = None
        if isinstance(response, dict) and hasattr(response, "get"):
            reference_id = response.get("reference_id", None)
        elif hasattr(response, "reference_id"):
            reference_id = getattr(response, "reference_id")

        print(f"\nAlınan reference_id: {reference_id}")

    except Exception as e:
        print(f"❌ Abonelik oluşturulurken hata: {e}")
        return

    # Eger abonelik referans id mevcut degilse islemleri sonlandir.
    if not reference_id:
        print(
            "⚠️ Geçerli bir Abonelik reference_id dönmediği için diğer adımlara geçilemiyor."
        )
        return

    # --- ADIM 2: ABONELİK DETAYI ALMA ---
    print_step(
        "Abonelik Detayı Getir (get_subscription)",
        f"Aboneliğin ({reference_id}) bilgileri API üzerinden alınacak.",
    )
    try:
        get_req = SubscriptionGetRequest(reference_id=reference_id)
        get_res = client.get_subscription(get_req)
        print("\n✅ Abonelik Detayı Yanıtı:")
        pretty_print(get_res)
    except Exception as e:
        print(f"❌ Abonelik detayı alınırken hata: {e}")

    # --- ADIM 3: ABONELİK İÇİN YÖNLENDİRME URL'Sİ ---
    print_step(
        "Abonelik Ödeme URL'si (redirect_subscription)",
        f"Aboneliğin ({reference_id}) ödeme işlemi için link oluşturulacak.",
    )
    try:
        redirect_req = SubscriptionRedirectRequest(subscription_id=reference_id)
        redirect_res = client.redirect_subscription(redirect_req)
        print("\n✅ Yönlendirme Yanıtı:")
        pretty_print(redirect_res)

        url_link = (
            redirect_res.get("url", redirect_res.get("redirect_url", None))
            if hasattr(redirect_res, "get")
            else getattr(redirect_res, "url", None)
        )

        if url_link:
            print("\n" + "*" * 60)
            print("💳 ABONELİK ÖDEME LİNKİ:")
            print(url_link)
            print(
                "Lütfen bu linke tıklayarak (veya tarayıcıya kopyalayarak) işlemi gerçekleştirin."
            )
            print("*" * 60 + "\n")
    except Exception as e:
        print(f"❌ Yönlendirme linki alınırken hata: {e}")

    # --- ADIM 4: ABONELİK İPTALİ ---
    print_step(
        "Abonelik İptali (cancel_subscription)",
        f"Abonelik ({reference_id}) sistemden iptal edilecek.",
    )
    try:
        cancel_req = SubscriptionCancelRequest(reference_id=reference_id)
        cancel_res = client.cancel_subscription(cancel_req)
        print("\n✅ Abonelik İptal Yanıtı:")
        pretty_print(cancel_res)
    except Exception as e:
        print(f"❌ Abonelik iptali sırasında hata: {e}")

    print("\n🎉 Tüm örnek abonelik akışı başarıyla tamamlandı!")


if __name__ == "__main__":
    main()
