# ===========================================================
# 🌍 TradeIntelliPro - Interactive Import-Export Calculator
# by Gnaneswar Somisetty
# ===========================================================

from abc import ABC, abstractmethod
import streamlit as st

# ------------------------------
# Exchange Rate Manager
# ------------------------------
class ExchangeManager:
    def __init__(self):
        self.rates = {
            "USD": 83.0,
            "EUR": 90.5,
            "AED": 22.6,
            "INR": 1.0
        } 

    def get_rate(self, currency):
        return self.rates.get(currency.upper(), 1.0)

    def convert(self, amount, from_currency, to_currency="INR"):
        rate = self.get_rate(from_currency) / self.get_rate(to_currency)
        return amount * rate

# ------------------------------
# Product Class
# ------------------------------
class Product:
    def __init__(self, name, hs_code, quantity, price_per_unit, currency):
        self.name = name
        self.hs_code = hs_code
        self.quantity = quantity
        self.price_per_unit = price_per_unit
        self.currency = currency

    def total_value(self):
        return self.quantity * self.price_per_unit

# ------------------------------
# Abstract Trade Class
# ------------------------------
class BaseTrade(ABC):
    def __init__(self, trade_type, exchange_manager: ExchangeManager):
        self.trade_type = trade_type
        self.exchange = exchange_manager
        self.products = []
        self.financials = {}
        self.logistics = {}
        self.misc_costs = {}

    def add_product(self, product: Product):
        self.products.append(product)

    def set_logistics(self, **kwargs):
        self.logistics = kwargs

    def set_financials(self, **kwargs):
        self.financials = kwargs

    def set_misc_costs(self, **kwargs):
        self.misc_costs = kwargs

    @abstractmethod
    def calculate_summary(self):
        pass

# ------------------------------
# Import Trade
# ------------------------------
class ImportTrade(BaseTrade):
    def __init__(self, exchange_manager):
        super().__init__("Import", exchange_manager)

    def calculate_summary(self):
        total_cif_inr = sum(
            self.exchange.convert(p.total_value(), p.currency, "INR") for p in self.products
        )

        logistics_total = sum(self.logistics.values())
        misc_total = sum(self.misc_costs.values())

        duty_rate = self.financials.get("customs_duty", 10)
        gst_rate = self.financials.get("gst", 18)
        finance_cost = self.financials.get("finance_interest", 0.02)
        commission = self.financials.get("commission", 0)
        margin = self.financials.get("margin", 20)

        customs_duty = total_cif_inr * duty_rate / 100
        gst = (total_cif_inr + customs_duty) * gst_rate / 100
        interest = total_cif_inr * finance_cost
        commission_amount = total_cif_inr * commission / 100

        landed_cost = total_cif_inr + logistics_total + misc_total + customs_duty + gst + interest + commission_amount
        selling_value = landed_cost * (1 + margin / 100)
        profit = selling_value - landed_cost

        return {
            "type": "Import",
            "total_cif": total_cif_inr,
            "landed_cost": landed_cost,
            "selling_value": selling_value,
            "profit": profit,
            "margin": (profit / landed_cost) * 100
        }

# ------------------------------
# Export Trade
# ------------------------------
class ExportTrade(BaseTrade):
    def __init__(self, exchange_manager):
        super().__init__("Export", exchange_manager)

    def calculate_summary(self):
        total_fob_inr = sum(
            self.exchange.convert(p.total_value(), p.currency, "INR") for p in self.products
        )

        logistics_total = sum(self.logistics.values())
        misc_total = sum(self.misc_costs.values())

        incentive_rate = self.financials.get("export_incentive", 5)
        tax_rebate = self.financials.get("tax_rebate", 3)
        bank_charges = self.financials.get("bank_charges", 0.5)
        commission = self.financials.get("commission", 2)
        margin = self.financials.get("margin", 25)

        incentive = total_fob_inr * incentive_rate / 100
        rebate = total_fob_inr * tax_rebate / 100
        commission_amount = total_fob_inr * commission / 100
        bank_fee = total_fob_inr * bank_charges / 100

        adjusted_cost = total_fob_inr + logistics_total + misc_total - incentive - rebate + commission_amount + bank_fee
        selling_value = adjusted_cost * (1 + margin / 100)
        profit = selling_value - adjusted_cost

        return {
            "type": "Export",
            "total_fob": total_fob_inr,
            "adjusted_cost": adjusted_cost,
            "selling_value": selling_value,
            "profit": profit,
            "margin": (profit / adjusted_cost) * 100
        }

# ------------------------------
# Portfolio
# ------------------------------
class TradePortfolio:
    def __init__(self, owner):
        self.owner = owner
        self.trades = []

    def add_trade(self, trade: BaseTrade):
        self.trades.append(trade)

    def portfolio_summary(self):
        total_profit = 0
        st.subheader(f"🌎 Trade Portfolio Summary: {self.owner}")
        for trade in self.trades:
            summary = trade.calculate_summary()
            total_profit += summary["profit"]
            st.markdown(f"### 🔹 {summary['type']} Trade Summary")
            st.write(summary)
        st.success(f"💰 Total Portfolio Profit: ₹{total_profit:,.2f}")

# ------------------------------
# Streamlit App
# ------------------------------
def main():
    st.title("🌍 TradeIntelliPro - Import/Export Calculator")
    ex = ExchangeManager()
    portfolio = TradePortfolio("Gnaneswar Somisetty")

    # ---------------- Currency Converter ----------------
    st.header("💱 Currency Converter")
    amount = st.number_input("Amount", min_value=0.0, value=1000.0)
    from_currency = st.selectbox("From Currency", ["USD", "EUR", "AED", "INR"], key="conv_from")
    to_currency = st.selectbox("To Currency", ["USD", "EUR", "AED", "INR"], key="conv_to")
    converted = ex.convert(amount, from_currency, to_currency)
    st.info(f"Converted Amount: {converted:,.2f} {to_currency}")

    # ---------------- Import Trade ----------------
    st.header("🟢 Import Trade")
    imp = ImportTrade(ex)
    with st.form("import_form"):
        num_products = st.number_input("Number of import products", min_value=1, max_value=10, value=2)
        import_products = []
        for i in range(num_products):
            st.markdown(f"**Product {i+1}**")
            name = st.text_input(f"Name {i+1}", key=f"imp_name_{i}")
            hs = st.text_input(f"HS Code {i+1}", key=f"imp_hs_{i}")
            qty = st.number_input(f"Quantity {i+1}", min_value=1, key=f"imp_qty_{i}")
            price = st.number_input(f"Price per Unit {i+1}", min_value=0.0, key=f"imp_price_{i}")
            currency = st.selectbox(f"Currency {i+1}", ["USD", "EUR", "AED", "INR"], key=f"imp_cur_{i}")
            if name:
                import_products.append(Product(name, hs, qty, price, currency))

        # Logistics, Misc, Financials
        st.subheader("Logistics & Misc Costs")
        freight = st.number_input("Freight", min_value=0.0, value=0.0)
        insurance = st.number_input("Insurance", min_value=0.0, value=0.0)
        port_handling = st.number_input("Port Handling", min_value=0.0, value=0.0)
        warehousing = st.number_input("Warehousing", min_value=0.0, value=0.0)
        demurrage = st.number_input("Demurrage", min_value=0.0, value=0.0)
        documentation = st.number_input("Documentation", min_value=0.0, value=0.0)
        transport = st.number_input("Transport", min_value=0.0, value=0.0)

        st.subheader("Financials")
        customs_duty = st.number_input("Customs Duty (%)", min_value=0.0, value=10.0)
        gst = st.number_input("GST (%)", min_value=0.0, value=18.0)
        finance_interest = st.number_input("Finance Interest (%)", min_value=0.0, value=1.5)/100
        commission = st.number_input("Commission (%)", min_value=0.0, value=1.0)
        margin = st.number_input("Margin (%)", min_value=0.0, value=25.0)

        submitted = st.form_submit_button("Calculate Import Trade")
        if submitted:
            for p in import_products:
                imp.add_product(p)
            imp.set_logistics(freight=freight, insurance=insurance, port_handling=port_handling,
                              warehousing=warehousing, demurrage=demurrage)
            imp.set_misc_costs(documentation=documentation, transport=transport)
            imp.set_financials(customs_duty=customs_duty, gst=gst,
                               finance_interest=finance_interest, commission=commission, margin=margin)
            portfolio.add_trade(imp)
            st.success("✅ Import Trade added to portfolio.")

    # ---------------- Export Trade ----------------
    st.header("🔵 Export Trade")
    exp = ExportTrade(ex)
    with st.form("export_form"):
        num_products = st.number_input("Number of export products", min_value=1, max_value=10, value=2, key="num_exp")
        export_products = []
        for i in range(num_products):
            st.markdown(f"**Product {i+1}**")
            name = st.text_input(f"Name {i+1}", key=f"exp_name_{i}")
            hs = st.text_input(f"HS Code {i+1}", key=f"exp_hs_{i}")
            qty = st.number_input(f"Quantity {i+1}", min_value=1, key=f"exp_qty_{i}")
            price = st.number_input(f"Price per Unit {i+1}", min_value=0.0, key=f"exp_price_{i}")
            currency = st.selectbox(f"Currency {i+1}", ["USD", "EUR", "AED", "INR"], key=f"exp_cur_{i}")
            if name:
                export_products.append(Product(name, hs, qty, price, currency))

        st.subheader("Logistics & Misc Costs")
        freight = st.number_input("Freight", min_value=0.0, value=0.0, key="exp_freight")
        insurance = st.number_input("Insurance", min_value=0.0, value=0.0, key="exp_insurance")
        port_handling = st.number_input("Port Handling", min_value=0.0, value=0.0, key="exp_port")
        warehousing = st.number_input("Warehousing", min_value=0.0, value=0.0, key="exp_ware")
        certification = st.number_input("Certification", min_value=0.0, value=0.0)
        packaging = st.number_input("Packaging", min_value=0.0, value=0.0)

        st.subheader("Financials")
        export_incentive = st.number_input("Export Incentive (%)", min_value=0.0, value=5.0)
        tax_rebate = st.number_input("Tax Rebate (%)", min_value=0.0, value=3.0)
        bank_charges = st.number_input("Bank Charges (%)", min_value=0.0, value=0.5)
        commission = st.number_input("Commission (%)", min_value=0.0, value=2.0)
        margin = st.number_input("Margin (%)", min_value=0.0, value=20.0)

        submitted = st.form_submit_button("Calculate Export Trade")
        if submitted:
            for p in export_products:
                exp.add_product(p)
            exp.set_logistics(freight=freight, insurance=insurance, port_handling=port_handling, warehousing=warehousing)
            exp.set_misc_costs(certification=certification, packaging=packaging)
            exp.set_financials(export_incentive=export_incentive, tax_rebate=tax_rebate,
                               bank_charges=bank_charges, commission=commission, margin=margin)
            portfolio.add_trade(exp)
            st.success("✅ Export Trade added to portfolio.")

    # ---------------- Portfolio Summary ----------------
    if portfolio.trades:
        portfolio.portfolio_summary()

if __name__ == "__main__":
    main()
