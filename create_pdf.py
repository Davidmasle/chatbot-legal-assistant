from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="Test PDF for Legal Assistant", ln=True)
pdf.multi_cell(0, 10, txt="Example text should be divided in chunks dasdadadadadasdadsadas")
pdf.output("sample.pdf")

print("PDF created: sample.pdf")
