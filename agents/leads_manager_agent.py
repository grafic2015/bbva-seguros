import json
from datetime import datetime, timedelta
from config import LEADS_FILE

class LeadsManager:
    def __init__(self):
        self.leads_file = LEADS_FILE

    def load_leads(self):
        """Carga los leads del archivo"""
        try:
            with open(self.leads_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"leads": [], "total_contacts": 0, "total_interested": 0}

    def save_leads(self, data):
        """Guarda los leads en archivo"""
        with open(self.leads_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def update_lead_status(self, username, status, respuesta=None):
        """Actualiza el estado de un lead"""
        data = self.load_leads()

        for lead in data["leads"]:
            if lead["usuario"] == username:
                lead["estado"] = status
                if respuesta:
                    lead["respuesta"] = respuesta
                lead["actualizado"] = datetime.now().isoformat()
                self.save_leads(data)
                print(f"✅ Lead @{username} actualizado a '{status}'")
                return True

        print(f"❌ Lead @{username} no encontrado")
        return False

    def get_leads_by_status(self, status):
        """Obtiene leads por estado"""
        data = self.load_leads()
        return [lead for lead in data["leads"] if lead["estado"] == status]

    def get_all_leads(self):
        """Obtiene todos los leads"""
        data = self.load_leads()
        return data["leads"]

    def get_stats(self):
        """Obtiene estadísticas de leads"""
        data = self.load_leads()
        leads = data["leads"]

        stats = {
            "total_contactados": len(leads),
            "nuevos": len([l for l in leads if l["estado"] == "nuevo"]),
            "interesados": len([l for l in leads if l["estado"] == "interesado"]),
            "en_seguimiento": len([l for l in leads if l["estado"] == "en_seguimiento"]),
            "convertidos": len([l for l in leads if l["estado"] == "convertido"]),
            "rechazados": len([l for l in leads if l["estado"] == "rechazado"])
        }
        return stats

    def print_dashboard(self):
        """Imprime un dashboard con las estadísticas"""
        stats = self.get_stats()
        print("\n" + "="*50)
        print("📊 DASHBOARD DE LEADS - SEGUROS AUTO")
        print("="*50)
        print(f"Total contactados: {stats['total_contactados']}")
        print(f"  🆕 Nuevos: {stats['nuevos']}")
        print(f"  👍 Interesados: {stats['interesados']}")
        print(f"  🔄 En seguimiento: {stats['en_seguimiento']}")
        print(f"  ✅ Convertidos: {stats['convertidos']}")
        print(f"  ❌ Rechazados: {stats['rechazados']}")
        print("="*50 + "\n")

if __name__ == "__main__":
    manager = LeadsManager()
    manager.print_dashboard()
