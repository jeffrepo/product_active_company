# Productos por empresa activa

Módulo genérico para **Odoo 17**. Propone la empresa activa al crear un producto
y permite elegir otra si el usuario tiene dos o más empresas seleccionadas en
el selector de empresas. Nombre técnico: `product_active_company`.

## Comportamiento

- Usa `env.company` como valor inicial. Por ejemplo, si el usuario está
  posicionado en B, el formulario propone B aunque A sea su empresa principal.
- Con **una sola empresa seleccionada**, el campo es de solo lectura durante la
  creación y el producto se asigna a esa empresa.
- Con **dos o más empresas seleccionadas**, permite elegir cualquiera de ellas y
  respeta la elección al guardar. Las empresas asignadas al usuario pero no
  seleccionadas no aparecen entre las opciones.
- Tener varias empresas asignadas y solo una seleccionada mantiene el bloqueo.
- Si no se indica una empresa o se deja vacía, asigna la activa. En importaciones
  y llamadas a la API aplica la misma regla: con varias empresas seleccionadas,
  conserva una empresa explícita habilitada y rechaza una que no esté habilitada.
- Cubre plantillas (`product.template`), productos (`product.product`), creación
  rápida, duplicación y creación por lotes.
- Una variante agregada a una plantilla existente conserva la empresa de esa
  plantilla, incluidos los productos compartidos. No cambia la empresa del
  producto existente por agregarle una variante.
- No modifica productos existentes al instalarse ni al editar otros campos.
  La edición posterior de la empresa sigue permitida entre las seleccionadas,
  sujeta a las restricciones estándar de Odoo.
- Respeta los permisos y reglas multiempresa de Odoo. No utiliza `sudo()`.

Los duplicados también proponen la empresa activa. En integraciones y procesos
internos, se debe ejecutar la operación con el contexto de empresa correspondiente
(`allowed_company_ids` o `with_company()`). Sin un contexto explícito, Odoo usa
la empresa principal como activa y las empresas asignadas como habilitadas.

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

Si ya estaba instalado, descargar los cambios, reiniciar Odoo y **actualizar**
el módulo desde Aplicaciones (o ejecutar `odoo-bin -d BASE -u product_active_company
--stop-after-init`). La versión `17.0.1.1.0` incorpora la selección de empresa.

## Verificación

Con un usuario con acceso a A, B y C:

1. Seleccionar solo B: al crear un producto, B aparece bloqueada.
2. Seleccionar A y B, con B activa: el formulario propone B y permite elegir A.
3. Guardar el producto eligiendo A: debe conservar A.
4. C no debe aparecer como opción mientras no esté seleccionada.

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
