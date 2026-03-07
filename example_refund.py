import os
import json

from tapsilat_py.client import TapsilatAPI
from tapsilat_py.models import RefundOrderDTO, RefundAllOrderDTO


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

    load_env(env_path)
    api_key = os.environ.get("TAPSILAT_API_KEY")
    if not api_key:
        print(f"HATA: API_KEY bulunamadı! '{env_path}' dosyasını kontrol edin.")
        return

    client = TapsilatAPI(api_key=api_key)

    print("\n" + "*" * 60)
    print("MOCK VERİ KULLANIMI")
    print(
        "Geliştirme/Test ortamında siparişlerin reference_id'lerini kullanmanız gerekir."
    )
    print("*" * 60 + "\n")

    print("Sistemdeki en son sipariş API'den çekiliyor...\n")
    try:
        orders_res = client.get_orders(per_page="1")
        rows = orders_res.get("rows", [])
        if rows:
            test_reference_id = rows[0].get("reference_id")
            print(
                f"✅ Otomatik olarak sistemdeki son sipariş ({test_reference_id}) seçildi!\n"
            )
        else:
            test_reference_id = "MOCK-REF-123"
            print("⚠️ Hiç sipariş bulunamadı, MOCK-REF-123 kullanılacak.\n")
    except Exception as e:
        test_reference_id = "MOCK-REF-123"
        print(f"⚠️ Sipariş çekilirken hata oluştu ({e}), MOCK-REF-123 kullanılacak.\n")

    # --- ADIM 1: KISMİ İADE ---
    print_step(
        "Kısmi İade (refund_order)",
        f"Sipariş ({test_reference_id}) için kısmi iade işlemi yapılacak (Örn: 50.0 TRY).",
    )
    try:
        refund_req = RefundOrderDTO(reference_id=test_reference_id, amount=50.0)
        response = client.refund_order(refund_req)
        print("\n✅ Kısmi İade Yanıtı:")
        pretty_print(response)
    except Exception as e:
        print(f"❌ Kısmi iade işlemi sırasında hata oluştu: {e}")

    # --- ADIM 2: TAM İADE ---
    print_step(
        "Tam İade (refund_all_order)",
        f"Sipariş ({test_reference_id}) için tüm tutarın iadesi yapılacak.",
    )
    try:
        refund_all_req = RefundAllOrderDTO(reference_id=test_reference_id)
        response = client.refund_all_order(refund_all_req)
        print("\n✅ Tam İade Yanıtı:")
        pretty_print(response)
    except Exception as e:
        print(f"❌ Tam iade işlemi sırasında hata oluştu: {e}")


if __name__ == "__main__":
    main()
