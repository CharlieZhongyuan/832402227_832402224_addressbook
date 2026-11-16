import io
from openpyxl import Workbook, load_workbook
from src.database import get_all_contacts, add_contact

def export_to_excel():
    """把所有联系人导出成 Excel 文件对象"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Contacts"
    ws.append(["姓名", "电话", "邮箱", "社交账号", "地址", "是否收藏"])

    contacts = get_all_contacts()
    for contact in contacts:
        phones = []
        emails = []
        socials = []
        addresses = []
        for m in contact["methods"]:
            if m["method_type"] == "phone":
                phones.append(m["method_value"])
            elif m["method_type"] == "email":
                emails.append(m["method_value"])
            elif m["method_type"] == "social":
                socials.append(m["method_value"])
            elif m["method_type"] == "address":
                addresses.append(m["method_value"])
        fav = "是" if contact["is_favorite"] else "否"
        ws.append([
            contact["name"],
            ";".join(phones),
            ";".join(emails),
            ";".join(socials),
            ";".join(addresses),
            fav
        ])

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer

def import_from_excel(file_content):
    """从 Excel 文件内容导入联系人，返回导入数量"""
    wb = load_workbook(io.BytesIO(file_content))
    ws = wb.active
    count = 0
    rows = list(ws.iter_rows(min_row=2, values_only=True))  # 跳过表头
    for row in rows:
        if not row or not row[0]:
            continue
        name = str(row[0]).strip()
        if not name:
            continue
        methods = []
        for cell in (row[1] or ""):
            pass
        phones = str(row[1] or "").split(";") if row[1] else []
        emails = str(row[2] or "").split(";") if row[2] else []
        socials = str(row[3] or "").split(";") if row[3] else []
        addresses = str(row[4] or "").split(";") if row[4] else []
        for p in phones:
            if p.strip():
                methods.append({"type": "phone", "value": p.strip()})
        for e in emails:
            if e.strip():
                methods.append({"type": "email", "value": e.strip()})
        for s in socials:
            if s.strip():
                methods.append({"type": "social", "value": s.strip()})
        for a in addresses:
            if a.strip():
                methods.append({"type": "address", "value": a.strip()})
        add_contact(name, methods)
        count += 1
    return count
