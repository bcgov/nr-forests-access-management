import { flushPromises, mount, shallowMount } from '@vue/test-utils'
import Breadcrumb from '@/components/Breadcrumb.vue'
import { it, describe, expect } from 'vitest'
import router from '@/router'
import { applicationsUserAdministers, selectedApplication } from '@/services/ApplicationState'
import type { Application } from '@/services/ApplicationState'


describe('Breadcrumb Component', () => {
  it('should be blank when home page', async () => {
    // const $router = { currentRoute: { value: { path: '/'}}}
    router.push('/')
    const wrapper = mount(Breadcrumb, {
      global: {
        plugins: [router]
        // mocks: {
        //   $router: $router
        // }

      }
    })
    await flushPromises()
    expect(wrapper.html()).toEqual('<span></span>')
  })

  it('should not show SelectApplication when user can administer only one app', () => {
    applicationsUserAdministers.value = [
      { application_name: 'FAKE', application_description: 'Fake Test App', application_id: 9999 }
    ] as Application[]
    selectedApplication.value = applicationsUserAdministers.value[0]

    router.push('/manage')
    const wrapper = mount(Breadcrumb, {
      global: {
        plugins: [router]
      }
    })
    expect(wrapper.html().includes("Select Application")).toBeFalsy()
  })

  it('should show SelectApplication when user can administer more than one app', async () => {
    applicationsUserAdministers.value = [
      { application_name: 'FAKE', application_description: 'Fake Test App', application_id: 9999 },
      { application_name: 'FAKE2', application_description: 'Fake 2 Test App', application_id: 9998 }
    ] as Application[]
    selectedApplication.value = applicationsUserAdministers.value[0]

    router.push('/manage')
    const wrapper = mount(Breadcrumb, {
      global: {
        plugins: [router]
      }
    })
    await flushPromises()
    expect(wrapper.html().includes("Select Application")).toBeTruthy()
  })

})

