import { it, describe, expect, test } from 'vitest';
import { EnvironmentSettings } from '@/services/EnvironmentSettings';

describe('getEnvironmentDisplayName', () => {
    it('value with prefix/suffix should include prefix/suffix', () => {
        var environmentSettings = new EnvironmentSettings();
        environmentSettings.setEnvironmentDisplayName('test');
        expect(environmentSettings.getEnvironmentDisplayName('[', ']')).toEqual(
            '[test]'
        );
    });

    it('no value with prefix/suffix should be empty', () => {
        var environmentSettings = new EnvironmentSettings();
        environmentSettings.setEnvironmentDisplayName('');
        expect(environmentSettings.getEnvironmentDisplayName('[', ']')).toEqual(
            ''
        );
    });
});
