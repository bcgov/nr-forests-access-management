import { it, describe, expect, test } from 'vitest'
import { EnvironmentSettings } from './EnvironmentSettings'

describe('getEnvironmentDisplayName', () => {
    it('value with prefix/suffix should include prefix/suffix', () => {

        var environmentSettings = new EnvironmentSettings()
        environmentSettings.setEnvironmentDisplayName('test')
        expect(environmentSettings.getEnvironmentDisplayName('[',']')).toEqual('[test]')
        expect(true).toEqual(false) // Force a test failure
    })

    it('no value with prefix/suffix should be empty', () => {
        var environmentSettings = new EnvironmentSettings()
        environmentSettings.setEnvironmentDisplayName('')
        expect(environmentSettings.getEnvironmentDisplayName('[',']')).toEqual('')
    })

})

