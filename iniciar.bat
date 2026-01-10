@echo off
set SUPABASE_HOST=aws-0-us-west-2.pooler.supabase.com
set SUPABASE_USER=postgres.emaktovavsuxvofltkbq
set SUPABASE_PASSWORD=asdl@colula70400
set SUPABASE_DB=postgres
set SUPABASE_PORT=5432

streamlit run app.py
```

Luego simplemente haz doble clic en `iniciar.bat`

---

### Opción 2: Configurar en el Sistema (Permanente)

1. Busca **"Variables de entorno"** en Windows
2. Click en **"Variables de entorno..."**
3. En **"Variables de usuario"**, click en **"Nueva..."**
4. Agrega cada variable:
   - Nombre: `SUPABASE_HOST`
   - Valor: `aws-0-us-west-2.pooler.supabase.com`
5. Repite para todas las variables
6. **Reinicia PowerShell** después

---

## 📸 ¿Qué Deberías Ver?

Después de configurar correctamente, en el **sidebar** deberías ver:
```
⚙️ Configuración
◉ Local (SQLite)
○ Remoto (Supabase)

✅ Supabase Conectado   ← Esto debería aparecer