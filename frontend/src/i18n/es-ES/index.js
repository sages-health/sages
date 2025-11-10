/*
*  Copyright (c) 2013-2025. The Johns Hopkins University Applied Physics Laboratory LLC
*
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* NO WARRANTY.   THIS MATERIAL IS PROVIDED "AS IS."  JHU/APL DISCLAIMS ALL
* WARRANTIES IN THE MATERIAL, WHETHER EXPRESS OR IMPLIED, INCLUDING (BUT NOT
* LIMITED TO) ANY AND ALL IMPLIED WARRANTIES OF PERFORMANCE,
* MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT OF
* INTELLECTUAL PROPERTY RIGHTS. ANY USER OF THE MATERIAL ASSUMES THE ENTIRE
* RISK AND LIABILITY FOR USING THE MATERIAL.  IN NO EVENT SHALL JHU/APL BE
* LIABLE TO ANY USER OF THE MATERIAL FOR ANY ACTUAL, INDIRECT,
* CONSEQUENTIAL, SPECIAL OR OTHER DAMAGES ARISING FROM THE USE OF, OR
* INABILITY TO USE, THE MATERIAL, INCLUDING, BUT NOT LIMITED TO, ANY DAMAGES
* FOR LOST PROFITS.
 */

export default {
  appName: 'SAGES',
  breadcrumb: {
    admin: 'Administración',
    alerts: 'Alertas',
    create: 'Crear',
    dashboard: 'Cuadro de Mandos',
    data: 'Datos',
    datasets: 'Conjuntos de Datos',
    datasources: 'Fuentes de Datos',
    manage: 'Gestionar',
    maps: 'Mapas',
    overlay: 'Superpuesta',
    users: 'Usuarios',
    groups: 'Grupos',
    views: 'Vistas',
    edit: 'Editar',
    visualization: 'Visualización',
    add: 'Añadir'
  },
  login: {
    username: 'Nombre de Usuario',
    password: 'Contraseña',
    otp: 'OTP',
    scanOtp: 'Escanea el código QR con la aplicación de autenticación',
    verifyOpt: 'Ingresa la OTP generada para verificar y habilitar la autenticación de dos factores con OTP',
    submit: 'Iniciar Sesiòn',
    forgotPassword: '¿Olvidaste tu contraseña?'
  },
  nav: {
    dashboard: {
      category: 'Cuadro de Mandos',
      new: 'Nuevo @:nav.dashboard.category',
      open: '@:common.open @:nav.dashboard.category'
    },
    visualization: {
      category: 'Visualización',
      new: 'Nueva @:nav.visualization.category',
      newOverlay: '@:common.new @:nav.visualization.category Superpuesta',
      open: '@:common.open @:nav.visualization.category',
      search: '@:common.search Visualizaciónes'
    },
    alerts: 'Alertas',
    data: {
      category: 'Datos'
    },
    dataset: {
      category: 'Conjuntos de Datos',
    },
    view: {
      category: 'Vistas'
    },
    datasource: {
      category: 'Fuentes de Datos'
    },
    map: {
      category: 'Mapas'
    },
    admin: {
      category: 'Administración',
      users: 'Usuarios',
      groups: 'Grupos'
    }
  },
  visualization: {
    type: 'Tipo de Visualización',
    included: 'Visualizaciones',
    add: 'Añadir Visualización',
    search: '@:common.search Visualizaciones',
    noneAvailable: 'No Hay Visualizaciones Disponibles',
    create: 'Crear Visualización',
    table: 'Tabla',
    line: 'Gráfico de Lineas',
    bar: 'Gráfico de Barras',
    pivot: 'Tabla Dinámica',
    pie: 'Gráfico Circular',
    map: 'Mapa',
    topN: 'N Más Altos',
    mappableField: 'Mapear Por',
    stratification: 'Estratificación',
    series: 'Series',
    barConfig: {
      stacked: "Apiladas",
      normalized: "Normalizado"
    },
    newYAxis: "Nuevo Eje Y",
    error: {
      noValidConfigurations: 'No hay configuraciones válidas.',
      noGroupBySelected: 'No se ha seleccionado ninguna X.',
      noAggregateFieldSelected: 'No se ha seleccionado Y.',
      notSupportedType: 'no se admite el tipo.',
      noDatasetSelected: 'No se ha seleccionado ningún conjunto de datos.'
    },
    timeResolution: 'Resolución de tiempo',
    detection: "Detecci\u00f3n",
    detectionWarning: "Advertencia (Detecci\u00f3n)",
    detectionError: "Error (Detecci\u00f3n)",
  },
  dashboard: {
    oneColumn: 'Una Columna',
    twoColumns: 'Dos Columnas',
    search: '@:common.search Cuadro de Mandos',
    noneAvailable: 'No Hay Cuadros De Mando Disponibles',
    create: 'Crear Cuadro de Mando',
    overrideDate: 'Proveer Nueva Fecha',
    autorefresh: 'Página de Actualización Automática',
    oneminute: "1 Minuto",
    fiveminutes: "5 Minutos",
    thirtyminutes: "30 Minutos",
    onehour: "1 Hora",
    updatetimetotal: "Temporizador",
    lastupdated: "Actualizado: "

},
  error: {
    valueOutOfBounds: 'Introduzca un valor entre '
  },
  common: {
    open: 'Abrir',
    view: 'Ver',
    grid: 'Cuadrícula',
    list: 'Lista',
    edit: 'Editar',
    cancel: 'Cancelar',
    delete: 'Borrar',
    apply: 'Aplicar',
    rowCount: 'Cuento de Filas',
    user: {
      single: 'Usuario',
      plural: 'Usuarios'
    },
    visualization: 'Visualización',
    title: 'Título',
    include: 'Incluir',
    saveAsNew: 'Guardar Como Nuevo',
    fetch: 'Buscar',
    fetchAll: 'Buscar Todos',
    fetchFiltered: 'Buscar Filtrado',
    addFilter: 'Añadir Filtro',
    confirm: 'Confirmar',
    save: 'Guardar',
    never: 'Nunca',
    add: 'Añadir',
    requiredField: 'Campo Obligatorio',
    field: {
      single: 'Campo',
      plural: 'Campos'
    },
    name: 'Nombre',
    description: 'Descripción',
    reference: 'Referencia',
    select: 'Seleccionar',
    selectAll: '@:common.select Todos',
    clear: 'Despejar',
    operator: 'Operador',
    value: 'Valor',
    and: 'Y',
    or: 'O',
    actions: 'Acciones',
    enabled: 'Habilitado',
    locked: 'Bloqueado',
    function: 'Función',
    search: 'Buscar',
    count: 'Contar',
    sum: 'Sumar',
    rows: 'Filas',
    min: 'Mínimo',
    max: 'Máximo',
    noData: 'No Hay Datos Disponibles',
    queryAggregateFunction: 'Función de Agregación',
    queryAggregateField: 'Campo Agregado',
    queryNumBins: 'Cubos',
    upload: 'Cargar',
    password: 'Contraseña',
    settings: 'Configuración',
    logout: 'Cerrar Sesión',
    locale: '',
    lastNBack: "Últimos N Días",
    last30Back: "Últimos 30 Días",
    last60Back: "Últimos 60 Días",
    last90Back: "Últimos 90 Días",
    last180Back: "Últimos 180 Días",
    last365Back: "Últimos 365 Días",
    unauthorized: "No Autorizado",
    day: 'Día',
    week: 'Semana',
    month: 'Mes',
    year: 'Año',
    epiweek: 'Epiweek',
  },
  dataset: {
    single: 'Conjunto de Datos',
    plural: 'Conjuntos de Datos',
    addDataSet: '@:common.add @:common.dataset.single',
    dataEntry: 'Etrada de Datos',
    search: 'Buscar @:dataset.plural',
    isActive: 'Está Activo',
    description: '@:dataset.single @:common.description',
    hiddenFields: '@:common.field.plural Ocultos',
    sharedFields: '@:common.field.plural Compartidos',
    fieldInfo: '@:common.field.single Información',
    fieldValues: '@:common.field.single Valores',
    filterValues: 'Valores de Filtrado',
    idField: 'ID @:common.field.single',
    displayName: 'Nombre para Mostrar',
    dataGranularity: 'Granularidad de Los Datos',
    isReference: 'Es @:common.reference',
    isMappable: 'Cartografiable',
    configureMapping: 'Configurar Mapa',
    selectMap: 'Seleccionar @:map.single',
    showMappedFieldValues: 'Mostrar Mapa',
    showUnmappedFieldValues: 'Mostrar sin Mapa',
    leftToMap: 'Campos Restantes Sin Mapear',
    multipleFieldsSelected: 'Varios @:common.field.plural Seleccionado',
    referenceValue: '@:common.reference Valor',
    referenceValueAlreadyAdded: '@:common.reference Valor Añadido',
    expirationDate: 'Fecha de Expiración',
    noneAvailable: 'No Hay Conjuntos de Datos Disponibles',
    create: 'Crear Conjunto de Datos',
    addallfields: 'Agregar todos los campos',
    removeallfields: 'Eliminar todos los campos',
    dateField: '@:common.field.single de Fecha Principal',
    datatype: "Tipo de Datos",
    text: "Texto",
    number: "Número",
    date: "Fecha"

},
  ops: {
    like: 'Así',
    likeCaseInsensitive: 'Así (No distingue mayúsculas de minúsculas)',
    notLike: 'No Así',
    notLikeCaseInsensitive: 'No Así (No distingue mayúsculas de minúsculas)',
    startsWith: 'Comienza Por',
    endsWith: 'Termina Con',
    contains: 'Contiene',
    equalTo: 'Igual A',
    notEqualTo: 'No Igual A',
    greaterThan: 'Superior A',
    greaterThanEqualTo: '@:ops.greaterThan / @:ops.equalTo',
    lessThan: 'Menos De',
    lessThanEqualTo: '@:ops.lessThan / @:ops.equalTo'
  },
  datasource: {
    single: 'Fuente de Datos',
    plural: 'Fuentes de Datos',
    pointOfContact: 'Punto de Contacto',
    type: 'Tipo',
    viewDataSets: 'Ver @:dataset.plural',
    addDataSet: 'Añadir @:dataset.single',
    search: 'Buscar @:datasource.plural',
  },
  map: {
    single: 'Mapa',
    plural: 'Mapas',
    addMap: 'Añadir @:map.single',
    search: 'Buscar @:map.plural',
    geoJsonFile: 'Archivo GeoJSON',
    geoJsonIdField: 'Campo GeoJSON ID'
  },
  region: {
    single: 'Región',
    plural: 'Regiones',
    addRegion: 'Añadir @:region.single',
    name: 'Nombre de @:region.single',
    geojson: '@:region.single GeoJSON',
    clearRegions: 'Despejar @:region.plural'
  },
  user: {
    username: 'Usuario',
    email: 'Correo Electrónico',
    firstName: 'Nombre',
    lastName: 'Apellido',
    role: 'Función',
    roles: 'Funciones',
    phoneNumber: 'Número de Teléfono',
    addUser: 'Añadir Usuario',
    password: '@:common.password',
    verifyPassword: 'Verificar @:common.password'
  },
  queryBuilder: {
    joinOperator: 'Operador de Unión'
  },
  usergroups: {
    usergroups: "Grupos de Usuarios",
    groups: "Grupos",
    groupName: "Nombre de Grupo",
    addGroup: "Crear Grupo"
  },
  data: {
    'uploading': 'Subiendo',
    'failed': 'Fallido',
    'success': 'Éxito',
    'running': 'Procesando',
    'notRunning': 'Seleccionar archivo para subir',
    'filename': 'Nombre de Archivo',
    'filetype': 'Tipo de Archivo',
    'submit': 'Enviar',
    'autoSuggest': 'Selección automática del tipo de archivo en función del nombre',
    'description': 'Descripción'
  },
  passwordReset: {
    'expiredMessage': 'Tu contraseña ha expirado. Por favor, crea una nueva.',
    'newPassword': 'Nueva contraseña',
    'confirmPassword': 'Confirmar nueva contraseña',
    'submit': 'Guardar nueva contraseña',
    'resetMessage': 'Ingresa una nueva contraseña'
  },
  forgotPassword: {
    "instruction": "Ingresa el nombre de usuario de la cuenta para restablecer la contraseña",
    "successMessage": "Se envió el enlace de restablecimiento de contraseña al correo electrónico asociado",
    "submit": "Enviar"
  }
}
