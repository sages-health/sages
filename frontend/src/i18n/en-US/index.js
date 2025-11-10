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
    admin: 'Admin',
    alerts: 'Alerts',
    create: 'Create',
    dashboard: 'Dashboard',
    data: 'Data',
    datasets: 'Data Sets',
    datasources: 'Data Sources',
    manage: 'Manage',
    maps: 'Maps',
    users: 'Users',
    groups: 'Groups',
    views: 'Views',
    edit: 'Edit',
    visualization: 'Visualization',
    workbench: 'Workbench',
    add: 'Add',
    upload: 'Upload'
  },
  login: {
    username: 'Username',
    password: 'Password',
    otp: 'OTP',
    scanOtp: 'Scan QR code with authenticator app',
    verifyOtp: 'Enter generated OTP to verify and enable OTP two-factor authentication',
    submit: 'Enter',
    forgotPassword: 'Forgot Password?'
  },
  nav: {
    dashboard: {
      category: 'Dashboard',
      new: 'New @:nav.dashboard.category',
      open: 'Open @:nav.dashboard.category'
    },
    workbench: {
      category: 'Workbench',
      new: 'New @:nav.workbench.category',
      open: 'Open @:nav.workbench.category'
    },
    visualization: {
      category: 'Visualization',
      new: 'New @:nav.visualization.category',
      newOverlay: 'New Overlay @:nav.visualization.category',
      open: 'Open @:nav.visualization.category',
      search: '@:common.search Visualizations'
    },
    alerts: 'Alerts',
    data: {
      category: 'Data',
      upload: 'Upload'
    },
    dataset: {
      category: 'Data Sets',
    },
    view: {
      category: 'Views'
    },
    datasource: {
      category: 'Data Sources'
    },
    map: {
      category: 'Maps'
    },
    admin: {
      category: 'Admin',
      users: 'Users'
    }
  },
  visualization: {
    included: 'Visualizations',
    type: 'Visualization Type',
    search: '@:common.search Visualizations',
    noneAvailable: 'No Visualizations Available',
    create: 'Create Visualization',
    add: 'Add Visualization',
    table: 'Table',
    line: 'Line Chart',
    bar: 'Bar Chart',
    pivot: 'Pivot Table',
    pie: 'Pie Table',
    map: 'Map',
    topN: 'Top n',
    mappableField: 'Map By',
    stratification: 'Stratification',
    series: 'Series',
    barConfig: {
      stacked: "Stacked",
      normalized: "Normalized"
    },
    newYAxis: "New Y Axis",
    error: {
      noValidConfigurations: 'No valid configurations.',
      noGroupBySelected: 'No X selected.',
      noAggregateFieldSelected: 'No Y selected.',
      notSupportedType: 'is not supported type',
      noDatasetSelected: 'No @:dataset.single selected.'
    },
    timeResolution: 'Time Resolution',
    detection: "Detection",
    algorithm: {
      CDC1: "CDC1",
      CDC2: "CDC2",
      CDC3: "CDC3",
      CUSUM: "CUSUM",
      EWMA: "EWMA",
    },
    detectionWarning: "Warning (Detection)",
    detectionError: "Error (Detection)"
  },
  dashboard: {
    oneColumn: 'One Column',
    twoColumns: 'Two Columns',
    search: '@:common.search Dashboard',
    noneAvailable: 'No Dashboards Available',
    create: 'Create Dashboard',
    overrideDate: 'Override Date',
    autorefresh: "Auto Refresh Dashboard",
    oneminute: "1 Minute",
    fiveminutes: "5 Minutes",
    thirtyminutes: "30 Minutes",
    onehour: "1 Hour",
    updatetimetotal: "Refresh Time",
    lastupdated: "Last Updated: "
  },
  error: {
    valueOutOfBounds: 'Please enter a value between '
  },
  common: {
    open: 'Open',
    view: 'View',
    grid: 'Grid',
    list: 'List',
    edit: 'Edit',
    cancel: 'Cancel',
    delete: 'Delete',
    apply: 'Apply',
    rowCount: 'Row Count',
    user: {
      single: 'User',
      plural: 'Users'
    },
    visualization: 'Visualization',
    title: 'Title',
    include: 'Include',
    saveAsNew: 'Save As New',
    fetch: 'Fetch',
    fetchAll: 'Fetch All',
    fetchFiltered: 'Fetch Filtered',
    addFilter: 'Add Filter',
    confirm: 'Confirm',
    save: 'Save',
    never: 'Never',
    add: 'Add',
    requiredField: 'Required Field',
    field: {
      single: 'Field',
      plural: 'Fields'
    },
    name: 'Name',
    description: 'Description',
    reference: 'Reference',
    select: 'Select',
    selectAll: '@:common.select All',
    clear: 'Clear',
    operator: 'Operator',
    value: 'Value',
    and: 'And',
    or: 'Or',
    actions: 'Actions',
    enabled: 'Enabled',
    locked: 'Locked',
    remote: 'Remote Instance',
    function: 'Function',
    search: 'Search',
    count: 'Count',
    sum: 'Sum',
    rows: 'Rows',
    min: 'Min',
    max: 'Max',
    noData: 'No Data Available',
    queryAggregateFunction: 'Aggregate Function',
    queryAggregateField: 'Aggregate Field',
    queryNumBins: 'Bins',
    settings: 'Settings',
    logout: 'Log Out',
    locale: 'Locale',
    lastNBack: "Last N Days",
    last30Back: "Last 30 Days",
    last60Back: "Last 60 Days",
    last90Back: "Last 90 Days",
    last180Back: "Last 180 Days",
    last365Back: "Last 365 Days",
    upload: 'Upload',
    error: 'Error',
    unauthorized: 'Unauthorized',
    day: 'Day',
    week: 'Week',
    month: 'Month',
    year: 'Year',
    days: 'Days',
    weeks: 'Weeks',
    months: 'Months',
    years: 'Years',
    epiweek: 'Epiweek',
    ageUnit: 'Age Unit',
    age: 'Age',
    number: 'Number'
  },
  dataset: {
    single: 'Data Set',
    plural: 'Data Sets',
    addDataSet: 'Add @:common:dataset.single',
    dataEntry: 'Data Entry',
    search: 'Search @:dataset.plural',
    isActive: 'Is Active',
    description: '@:dataset.single @:common.description',
    hiddenFields: 'Hidden @:common.field.plural',
    sharedFields: 'Shared @:common.field.plural',
    fieldInfo: '@:common.field.single Info',
    fieldValues: '@:common.field.single Values',
    filterValues: 'Filter Values',
    idField: 'ID @:common.field.single',
    dateField: 'Primary Date @:common.field.single',
    displayName: 'Display Name',
    dataGranularity: 'Data Granularity',
    isReference: 'Is @:common.reference',
    isMappable: 'Mappable',
    configureMapping: 'Configure Map',
    selectMap: 'Select @:map.single',
    showMappedFieldValues: 'Show Mapped',
    showUnmappedFieldValues: 'Show Unmapped',
    leftToMap: 'Left to Map',
    multipleFieldsSelected: 'Multiple @:common.field.plural Selected',
    referenceValue: '@:common.reference Value',
    referenceValueAlreadyAdded: '@:common.reference Value Already Added',
    expirationDate: 'Expiration Date',
    noneAvailable: 'No Datasets Available',
    create: 'Create Dataset',
    titleExists: 'Dataset with specified title exists',
    titleError: 'Please provide a unique dataset title.',
    addallfields: 'Add All Fields',
    removeallfields: 'Remove All Fields',
    datatype: "Data Type",
    text: "Text",
    number: "Number",
    date: "Date"
  },
  ops: {
    like: 'Like',
    likeCaseInsensitive: 'Like (case insensitive)',
    notLike: 'Not Like',
    notLikeCaseInsensitive: 'Not Like (Case Insensitive)',
    startsWith: 'Starts With',
    endsWith: 'Ends With',
    contains: 'Contains',
    equalTo: 'Equal To',
    notEqualTo: 'Not Equal To',
    greaterThan: 'Greater Than',
    greaterThanEqualTo: '@:ops.greaterThan / @:ops.equalTo',
    lessThan: 'Less Than',
    lessThanEqualTo: '@:ops.lessThan / @:ops.equalTo'
  },
  datasource: {
    single: 'Data Source',
    plural: 'Data Sources',
    pointOfContact: 'Point of Contact',
    datasourceType: '@:datasource.single Type',
    displayName: 'Display Name',
    pointOfContactEmail: 'Point of Contact Email',
    create: 'Create @:datasource.single',
    noneAvailable: 'No @:datasource.plural Available',
    viewDataSets: 'View @:dataset.plural',
    addDataSet: 'Add @:dataset.single',
    search: 'Search @:datasource.plural',
    connectionUrl: 'Connection URL',
    password: 'Password',
    ssl: 'SSL',
    minConnectionSize: 'Minimum Connection Pool Size',
    maxConnectionSize: 'Maximum Connection Pool Size',
    dataSourceWorkerHealthy: '@:datasource.single Healthy or Online',
    username: 'Username',
    testConnection: 'Test Connection'
  },
  map: {
    single: 'Map',
    plural: 'Maps',
    addMap: 'Add @:map.single',
    search: 'Search @:map.plural',
    geoJsonFile: 'GeoJSON File',
    geoJsonIdField: 'GeoJSON ID Field'
  },
  region: {
    single: 'Region',
    plural: 'Regions',
    addRegion: 'Add @:region.single',
    name: '@:region.single Name',
    geojson: '@:region.single GeoJSON',
    clearRegions: 'Clear @:region.plural'
  },
  user: {
    accountExists: 'Username already exists',
    passwordRequirement: 'Password must be longer than 12 characters.',
    passwordComplexityRequirement: 'Password must include a mix of uppercase and lowercase letters, numbers, and symbols',
    passwordsMustMatch: 'Password fields must match',
    emailRequirement: 'Invalid email address',
    username: 'Username',
    email: 'Email',
    organization: 'Organization',
    firstName: 'First Name',
    lastName: 'Last Name',
    role: 'Role',
    roles: 'Roles',
    phoneNumber: 'Phone Number',
    addUser: 'Add User',
    password: 'Password',
    verifyPassword: 'Verify Password'
  },
  queryBuilder: {
    joinOperator: 'Join Operator'
  },
  usergroups: {
    usergroups: "User Groups",
    groups: "Groups",
    groupName: "Group Name",
    addGroup: "Add Group"
  },
  data: {
    'uploading': 'Uploading',
    'failed': 'Failed',
    'success': 'Success',
    'running': 'Processing',
    'notRunning': 'Select File to Upload',
    'filename': 'File Name',
    'filetype': 'File Type',
    'submit': 'Submit',
    'autoSuggest': 'Auto-Select File Type Based On Name',
    'description': 'dDescripción'
  },
  passwordReset: {
    'expiredMessage': 'Password has expired. Please make a new password.',
    'newPassword': 'New Password',
    'confirmPassword': 'Verify New Password',
    'submit': 'Set New Password',
    'resetMessage': 'Enter new password'
  },
  forgotPassword: {
    'instruction': "Enter username of account to reset password",
    'successMessage': "Sent password reset link to associated email",
    'submit': "Submit"
  }

}
