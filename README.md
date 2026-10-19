# Productos por empresa activa

Módulo genérico para **Odoo 17**. Asigna cada producto nuevo a la empresa activa
del usuario en el selector de empresas, independientemente de cuántas empresas
tenga asignadas o habilitadas. Nombre técnico: `product_active_company`.

## Comportamiento

- Usa `env.company`, la empresa activa de la operación. Por ejemplo, si el usuario
  tiene las empresas A, B y C y está posicionado en B, el producto pertenece a B,
  aunque A sea la empresa principal configurada en su usuario.
- Muestra la empresa activa al abrir el formulario de un producto nuevo. El campo
  es de solo lectura durante la creación.
- Aplica la asignación al guardar, incluso si el formulario, una importación o una
  llamada a la API envía otra empresa o deja el campo vacío.
- Cubre plantillas (`product.template`), productos (`product.product`), creación
  rápida, duplicación y creación por lotes.
- Una variante agregada a una plantilla existente conserva la empresa de esa
  plantilla, incluidos los productos compartidos. No cambia la empresa del
  producto existente por agregarle una variante.
- No modifica productos existentes al instalarse ni al editar otros campos.
  La edición posterior de la empresa conserva el comportamiento estándar de Odoo.
- Respeta los permisos y reglas multiempresa de Odoo. No utiliza `sudo()`.

La regla es obligatoria para **productos nuevos**: para crearlos en otra empresa,
hay que cambiar primero la empresa activa. En integraciones y procesos internos,
se debe ejecutar la operación con el contexto de empresa correspondiente
(`allowed_company_ids` o `with_company()`). Sin un contexto explícito, Odoo usa
la empresa principal del usuario.

## Instalación

1. Clonar este repositorio en una carpeta llamada `product_active_company` dentro
   de un directorio de módulos personalizados, por ejemplo:

   ```sh
   git clone https://github.com/jeffrepo/product_active_company.git /opt/odoo/custom-addons/product_active_company
   ```

2. Agregar `/opt/odoo/custom-addons` al `addons_path` de Odoo y reiniciar el servicio.
3. Activar el modo desarrollador y actualizar la lista de aplicaciones.
4. Buscar `product_active_company`, quitando el filtro «Aplicaciones» si es
   necesario, e instalar **Productos por empresa activa**.

Solo depende del módulo estándar `product`; no requiere módulos de JCDecaux.
No tiene parámetros de configuración ni ejecuta una migración de productos.

## Verificación

Con un usuario con acceso a dos o tres empresas, seleccionar una empresa activa
distinta de la principal y crear un producto. Su empresa debe coincidir con la
activa. Cambiar la empresa activa y repetir la creación.

Las pruebas de integración cubren usuarios con una, dos y tres empresas,
formularios, valores explícitos/contextuales, importación, duplicación, creación
rápida y por lotes, variantes existentes y permisos. GitHub Actions instala el
módulo en Odoo 17 con PostgreSQL y ejecuta estas pruebas en cada cambio.

Para ejecutarlas en una base de pruebas local:

```sh
odoo-bin -d product_active_company_test \
  --addons-path=/ruta/odoo/addons,/ruta/custom-addons \
  -i product_active_company --without-demo=all \
  --test-enable --test-tags=/product_active_company --stop-after-init
```

## Licencia

LGPL-3.
