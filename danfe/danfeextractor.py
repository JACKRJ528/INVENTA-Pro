import xml.etree.ElementTree as ET

class DANFE:
    def extrair_itens_danfe(self,xml_path):
        tree = ET.parse(xml_path)
        root = tree.getroot()

        namespace = {'ns': 'http://www.portalfiscal.inf.br/nfe'}  # padrão do XML da NF-e
        produtos = []

        for det in root.findall(".//ns:det", namespace):
            codigo = det.find("ns:prod/ns:cProd", namespace).text
            nome = det.find("ns:prod/ns:xProd", namespace).text
            quantidade = float(det.find("ns:prod/ns:qCom", namespace).text)
            unidade = det.find("ns:prod/ns:uCom", namespace).text
            valor_unitario = float(det.find("ns:prod/ns:vUnCom", namespace).text)

            produtos.append({
                'codigo': codigo,
                'nome': nome,
                'quantidade': quantidade,
                'unidade': unidade,
                'valor_unitario': valor_unitario
            })

        return produtos

    def salvar_produtos(self,produtos, db_path="db/inventa.db"):
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        for item in produtos:
            cursor.execute("""
                INSERT INTO produtos (codigo, nome, quantidade, unidade, valor_unitario)
                VALUES (?, ?, ?, ?, ?)
            """, (item['codigo'], item['nome'], item['quantidade'], item['unidade'], item['valor_unitario']))

        conn.commit()
        conn.close()