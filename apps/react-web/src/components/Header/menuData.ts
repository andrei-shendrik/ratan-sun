export interface SubMenuItem { labelKey: string; path: string; external?: boolean; }
export interface SubMenuGroup { groupLabelKey: string; items: SubMenuItem[]; }
export interface SubMenuColumn { groups: SubMenuGroup[]; }
export interface MenuItem { key: string; labelKey: string; path?: string; subColumns?: SubMenuColumn[]; }

export const MENU_ITEMS: MenuItem[] = [
    { key: 'home', labelKey: 'menu.home', path: '/' },
    {
        key: 'observations', labelKey: 'menu.observations.title',
        subColumns: [
            { // столбец 1
                groups: [{
                    groupLabelKey: 'menu.observations.groups.solar',
                    items: [
                        { labelKey: 'menu.observations.items.latest', path: '/latest-observations' },
                        { labelKey: 'menu.observations.items.archive', path: 'https://solar.sao.ru/data', external: true },
                        { labelKey: 'menu.observations.items.schedule', path: '/observation-schedule' }
                    ]
                }]
            },
            { // столбец 2
                groups: [{
                    groupLabelKey: 'menu.observations.groups.selection',
                    items: [
                        { labelKey: 'menu.observations.items.fast_acq_1_3', path: '/select-of-observation-fast-acq-1-3ghz' },
                        { labelKey: 'menu.observations.items.sspc', path: '/select-of-observation-sspc-3-18ghz' }
                    ]
                }]
            }
        ]
    },
    {
        key: 'resources', labelKey: 'menu.resources.title',
        subColumns: [{
            groups: [
                {
                    groupLabelKey: 'menu.resources.groups.general',
                    items: [
                        { labelKey: 'menu.resources.items.prognoz', path: 'http://spbf.sao.ru/prognoz', external: true },
                        { labelKey: 'menu.resources.items.sao', path: 'https://www.sao.ru/', external: true },
                        { labelKey: 'menu.resources.items.jets', path: '/coronal-jets-catalog', external: true },
                        { labelKey: 'menu.resources.items.dataview', path: '/dataview/', external: true }
                    ]
                },
                {
                    groupLabelKey: 'menu.resources.groups.software',
                    items: [
                        { labelKey: 'menu.resources.items.ratanpy', path: 'https://github.com/andrei-shendrik/ratanpy', external: true }
                    ]
                }
            ]
        }]
    },
    {
        key: 'about', labelKey: 'menu.about.title',
        subColumns: [
            {
                groups: [{
                    groupLabelKey: 'menu.about.groups.instrument',
                    items: [
                        { labelKey: 'menu.about.items.telescope', path: '/telescope' },
                        { labelKey: 'menu.about.items.receivers', path: '/receivers' }
                    ]
                }]
            },
            {
                groups: [
                    {
                        groupLabelKey: 'menu.about.groups.about_us',
                        items: [{ labelKey: 'menu.about.items.branch', path: '/about-us' }]
                    },
                    {
                        groupLabelKey: 'menu.about.groups.science',
                        items: [{ labelKey: 'menu.about.items.publications', path: '/publications' }]
                    }
                ]
            }
        ]
    },
    { key: 'contacts', labelKey: 'menu.contacts', path: '/contacts' },
];