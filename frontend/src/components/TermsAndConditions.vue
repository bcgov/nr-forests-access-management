<script lang="ts" setup>
import CheckIcon from "@carbon/icons-vue/es/checkmark/16";
import { AppActlApiService } from "@/services/ApiServiceFactory";
import useAuth from "@/composables/useAuth";
import {
    hideTerms,
    isTermsCloseable,
    isTermsVisible,
} from "@/store/TermsAndConditionsState";
import Dialog from "primevue/dialog";
import { useMutation, useQueryClient } from "@tanstack/vue-query";
import Button from "@/components/UI/Button.vue";

const auth = useAuth();

/*
Note: about Terms and Conditions used in coding.
    Ther current version of T&C file is : "2024-06-04-.FAM.terms.of.use.approved.by.WK.BB.pdf".
    Contact Olga or Kajo for the latest copy. Right now its not being stored in central place.
    If there is version update, developers need to be aware the changes needs to be on both
    frontend and the backend (GC Notify email sending for delegated admin has T&C as a link)
*/

const queryClient = useQueryClient();

const acceptTermsAndConditionsMutation = useMutation({
    mutationFn: () =>
        AppActlApiService.userTermsAndConditionsApi.createUserTermsAndConditions(),
    onSuccess: () => {
        queryClient.refetchQueries({
            queryKey: ["user_terms_conditions", "user:validate"],
        });
        hideTerms();
    },
    onError: (error) => {
        console.error("Accept terms and conditions failed: ", error);
        auth.logout();
    },
});

const acceptTermsAndConditions = () => {
    acceptTermsAndConditionsMutation.mutate();
};
</script>

<template>
    <Dialog
        class="terms-and-conditions-container"
        v-model:visible="isTermsVisible"
        header="FAM Terms of use"
        :closable="isTermsCloseable"
        modal
        @close="hideTerms()"
        :style="{ 'min-width': '50vw' }"
        :pt="{
            title: {
                style: {
                    'font-size': '1.25rem',
                },
            },
        }"
    >
        <div
            class="terms"
            :style="
                !isTermsCloseable
                    ? 'padding: 1rem 0;'
                    : 'padding: 0; padding-top: 1rem;'
            "
        >
            <p>
                This Forest Access Management application (“FAM”) terms of use
                agreement (the "Agreement") is entered into between the legal
                entity that has received approval for Delegated Administrator
                access to FAM (the “Subscriber”) and His Majesty the King in
                right of the Province of British Columbia as represented by the
                Minister of Forests (the “Province").
            </p>
            <p>
                By clicking the “I Accept” button (or any similar button or
                mechanism), and in consideration of the Province granting the
                Delegated Administrator access to FAM, the Subscriber, and the
                Delegated Administrator on behalf of the Subscriber, agree (and
                will be conclusively deemed to have agreed) to the following:
            </p>

            <ol type="1" class="terms-list">
                <h3>Definitions</h3>
                <li>
                    In this Agreement the following words have the following
                    meanings:
                </li>
                <ol type="a">
                    <li>
                        "Applications” means any applications to which Users may
                        be granted access by the Delegated Administrator through
                        FAM;
                    </li>
                    <li>
                        “Business BCeID” means the Master Login ID and User
                        Login IDs (both as defined in the Business BCeID Terms)
                        issued to the Subscriber and individuals within the
                        Subscriber's organization pursuant to the Business BCeID
                        Terms;
                    </li>
                    <li>
                        “Business BCeID Terms” means the terms found at:
                        <a
                            target="_blank"
                            href="https://www.bceid.ca/aboutbceid/agreements.aspx"
                            >https://www.bceid.ca/aboutbceid/agreements.aspx</a
                        >;
                    </li>
                    <li>
                        “Delegated Administrator” means the individual within
                        the Subscriber's organization who is responsible for
                        granting Users access to Applications through FAM;
                    </li>
                    <li>
                        “Device” means a computer, mobile device or any other
                        device capable of accessing FAM or any Application;
                    </li>
                    <li>
                        “Documentation” means documentation for FAM or an
                        Application that describes the features and
                        functionality of FAM or the Application;
                    </li>
                    <li>
                        “FOIPPA” means the Freedom of Information and Protection
                        of Privacy Act, R.S.B.C. 1996, c. 165, as amended or
                        replaced from time to time;
                    </li>
                    <li>
                        “Users” means individuals within the Subscriber's
                        organization who have been granted access to any
                        Application by the Delegated Administrator through FAM;
                        and
                    </li>
                    <ol type="i">
                        <li>
                            “Works” means, collectively, FAM, the Applications
                            and the Documentation.
                        </li>
                    </ol>
                </ol>

                <h3>Authority and Ability to Accept Terms</h3>
                <li>
                    The Delegated Administrator accepting the terms of this
                    Agreement on behalf of the Subscriber represents and
                    warrants that:
                </li>
                <ol class="subsection" type="a">
                    <li>they are at least 19 years of age; and</li>
                    <li>
                        they have all necessary authority to accept this
                        Agreement on behalf of the Subscriber.
                    </li>
                </ol>

                <h3>Responsibilities of Subscriber</h3>
                <li>
                    The Subscriber acknowledges and agrees that it is
                    responsible for ensuring that:
                </li>
                <ol class="subsection" type="a">
                    <li>
                        the Delegated Administrator and Users have all necessary
                        hardware and software required to allow the Delegated
                        Administrator to access FAM and to allow Users to access
                        the Applications;
                    </li>
                    <li>
                        the Delegated Administrator fulfills the
                        responsibilities set out in section 4 of this Agreement;
                    </li>
                    <li>
                        the Subscriber takes such steps as are necessary to
                        ensure that any individual that leaves the Subscriber's
                        organization no longer has access to FAM or any
                        Application;
                    </li>
                    <li>
                        the Subscriber takes appropriate steps regarding the
                        security of any Device used to access FAM or any
                        Applications, including as applicable informing Users
                        that FAM and the Applications must not be accessed using
                        publicly shared Devices, that Devices used to access FAM
                        or any Application must be kept up to date, and that
                        appropriate security measures such as setting Devices
                        used to access FAM or any Application to lock after a
                        short period of inactivity must be observed;
                    </li>
                    <li>
                        Users are made aware of the terms of this Agreement
                        applicable to them; and
                    </li>
                    <li>
                        the Delegated Administrator and Users comply with all
                        applicable laws, any applicable Documentation, and the
                        terms of this
                    </li>
                </ol>

                <h3>Agreement applicable to them.</h3>
                <li>Responsibilities of Delegated Administrator</li>
                <li>
                    The Delegated Administrator is responsible for managing User
                    access to the Applications, including:
                </li>
                <ol class="subsection" type="a">
                    <li>
                        managing the process for granting Users access to the
                        Applications;
                    </li>
                    <li>
                        ensuring that Users have the minimum level of access to
                        Applications that is necessary to perform their job
                        functions;
                    </li>
                    <li>
                        promptly revoking access for any User who:
                        <ol type="i">
                            <li>
                                no longer requires access to perform the User's
                                job functions,
                            </li>
                            <li>leaves the Subscriber's organization, or</li>
                            <li>
                                fails to comply with any term of this Agreement
                                applicable to Users; and
                            </li>
                        </ol>
                    </li>
                    <li>
                        ensuring that the list of Users remains accurate and up
                        to date.
                    </li>
                </ol>

                <h3>Authentication</h3>
                <li>The Subscriber acknowledges and agrees that:</li>
                <ol type="a" class="subsection">
                    <li>
                        the Delegated Administrator and Users will use the
                        Subscriber's Business BCeID to authenticate their
                        identity before access is granted to FAM (in the case of
                        the Delegated Administrator) or any Application (in the
                        case of Users);
                    </li>
                    <li>
                        the Subscriber is responsible for all use of its
                        Business BCeID; and
                    </li>
                    <li>
                        the Business BCeID Terms continue to apply to the
                        Subscriber, the Delegated Administrator and Users.
                    </li>
                </ol>

                <h3>Collection of Information</h3>
                <li>
                    Contact information (as defined in FOIPPA) consisting of
                    first and last name and business email address is collected
                    from the Delegated Administrator and Users in connection
                    with the use of FAM and the Applications. This information
                    is used for the purposes of providing access to and of
                    managing the ongoing operation and administration of FAM and
                    the Applications. Any information automatically collected
                    from individuals through the website through which FAM and
                    the Applications are accessed is collected in accordance
                    with the Province's general
                    <a
                        target="_blank"
                        href="https://www2.gov.bc.ca/gov/content/home/privacy"
                        >Privacy Policy</a
                    >.
                </li>

                <h3>Ownership and License</h3>
                <li>
                    The Works are owned by the Province or its licensors and are
                    protected by copyright, trademark and other laws protecting
                    intellectual property rights. Use of the Works except as
                    expressly permitted under this Agreement or as otherwise
                    approved by the Province in writing is prohibited
                </li>
                <li>
                    The Province grants to the Delegated Administrator a
                    non-exclusive, revocable, limited license to access and use
                    FAM, and to allow Users to access and use the Applications
                    and the Documentation, in accordance with the terms of this
                    Agreement.
                </li>
                <li>
                    A User's right to access and use the Applications and the
                    Documentation automatically terminates if the User's access
                    is revoked by the Delegated Administrator pursuant to
                    section 4. The Delegated Administrator's right to access and
                    use FAM is:
                </li>
                <ol type="a">
                    <li>
                        automatically suspended if the Delegated Administrator's
                        access to FAM is suspended pursuant to section 11; and
                    </li>
                    <li>
                        automatically terminated if the Delegated
                        Administrator's access to FAM is terminated by the
                        Province pursuant to section 11.
                    </li>
                </ol>

                <h3>Acceptable Use</h3>
                <li>
                    The Subscriber must not take, and must ensure that the
                    Delegated Administrator and Users do not take, any action
                    that would jeopardize the security, integrity and/or
                    availability of FAM or any Application, including:
                </li>
                <ol type="a" class="subsection">
                    <li>
                        using FAM or any Application for any unlawful or
                        inappropriate purpose;
                    </li>
                    <li>
                        decompiling, disassembling, reverse engineering or
                        otherwise copying any software associated with FAM or
                        any Application;
                    </li>
                    <li>
                        tampering with any portion of FAM or any Application;
                    </li>
                    <li>
                        using FAM or any Application to transmit any virus or
                        other harmful or destructive computer code, files or
                        programs or to conduct hacking and/or intrusion
                        activities;
                    </li>
                    <li>
                        attempting to circumvent or subvert any security measure
                        associated with FAM or any Application;
                    </li>
                    <li>
                        taking any action that might reasonably be construed as
                        likely to adversely affect other users of FAM or any
                        Application; or
                    </li>
                    <li>
                        removing or altering any proprietary symbol or notice,
                        including any copyright notice, trademark or logo,
                        displayed in connection with the Works.
                    </li>
                </ol>

                <h3>Suspension and Termination</h3>
                <li>The Province may, in its sole discretion:</li>
                <ol class="subsection">
                    <li>
                        immediately suspend the Delegated Administrator's access
                        to FAM if:
                        <ol type="i">
                            <li>
                                the Delegated Administrator breaches any
                                provision of this Agreement applicable to the
                                Delegated Administrator, or
                            </li>
                            <li>
                                the Province determines, in its sole discretion
                                that such suspension is necessary to maintain
                                the security, integrity, or availability of FAM
                                or any other aspect of the Province's systems;
                            </li>
                        </ol>
                    </li>
                    <li>
                        restore the Delegated Administrator's access if the
                        reason for the suspension is resolved to the Province's
                        satisfaction; and
                    </li>
                    <li>
                        terminate the Delegated Administrator's access if:
                        <ol type="i">
                            <li>
                                the reason for the suspension is not resolved to
                                the Province's satisfaction, or
                            </li>
                            <li>
                                the Delegated Administrator leaves the
                                Subscriber's organization.
                            </li>
                        </ol>
                    </li>
                </ol>

                <h3>Indemnification</h3>
                <div class="terms-list">
                    <li>
                        The Subscriber must indemnify and save harmless the
                        Province and the Province's employees and agents from
                        any loss, claim (including any claim of infringement of
                        third-party intellectual property rights), damage award,
                        action, cause of action, cost or expense that the
                        Province or any of the Province's employees or agents
                        may sustain, incur, suffer or be put to at any time,
                        either before or after this Agreement ends (each a
                        “Loss”), to the extent the Loss is directly or
                        indirectly caused or contributed to by any act or
                        omission by the Subscriber, the Delegated Administrator,
                        any User or any other employee, officer, agent or
                        director of the Subscriber in connection with this
                        Agreement.
                    </li>

                    <h3>Disclaimer</h3>
                    <li>
                        The Works are provided “as is”, and the Province
                        disclaims all representations, warranties, conditions,
                        obligations and liabilities of any kind, whether express
                        or implied, in relation to the Works, including but not
                        limited to implied warranties with respect to fitness
                        for a particular purpose, merchantability, satisfactory
                        quality, and non-infringement. Without limiting the
                        general nature of the previous sentence, the Province
                        does not represent or warrant the accuracy or the
                        completeness of the Works or any information or data
                        contained within the Works, that FAM or the Applications
                        will function without error, failure, or interruption,
                        or that the Works will meet the Subscriber's
                        expectations or requirements. This disclaimer applies in
                        addition to the Province's general
                        <a
                            target="_blank"
                            href="https://www2.gov.bc.ca/gov/content/home/disclaimer"
                        >
                            Warranty Disclaimer </a
                        >.
                    </li>

                    <h3>Limitation of Liability</h3>
                    <li>
                        To the maximum extent permitted by applicable law, under
                        no circumstances will the Province be liable to any
                        person or entity for any direct, indirect, special,
                        incidental, consequential or other loss, claim, injury
                        or damage, whether foreseeable or unforeseeable
                        (including without limitation claims for damages for
                        loss of profits or business opportunities, use or misuse
                        of, or inability to use, the Works, interruptions,
                        deletion or corruption of files, loss of programs or
                        information, errors, defects or delays), arising out of
                        or in any way connected with the use of the Works and
                        whether based on contract, tort, strict liability or any
                        other legal theory. The previous sentence will apply
                        even if the Province has been specifically advised of
                        the possibility of any such loss, claim, injury or
                        damage. This limitation of liability applies in addition
                        to the Province's general
                        <a
                            target="_blank"
                            href="https://www2.gov.bc.ca/gov/content/home/disclaimer"
                            >Limitation of Liabilities</a
                        >.
                    </li>

                    <h3>Changes to FAM and/or this Agreement</h3>
                    <li>
                        The Province may at any time, in its sole discretion,
                        make changes to the Works and/or the terms and
                        conditions of this Agreement. The Delegated
                        Administrator will be notified upon sign in to FAM if
                        changes have been made to the terms and conditions of
                        this Agreement, and must accept the updated terms and
                        conditions by clicking the “I Accept” button (or similar
                        button or mechanism) in order to proceed. By proceeding,
                        the Subscriber, and the Delegated Administrator on
                        behalf of the Subscriber, will be conclusively deemed to
                        have accepted the updated terms and conditions.
                    </li>

                    <h3>General</h3>
                    <li>In this Agreement:</li>
                    <ol type="a" class="subsection">
                        <li>
                            words expressed in the singular include the plural
                            and vice versa; and
                        </li>
                        <li>“including” is not intended to be limiting.</li>
                    </ol>
                    <li>
                        This Agreement, and any terms for which links are
                        provided in this Agreement, is the entire agreement
                        between the Subscriber and the Province with respect to
                        the use of the Works.
                    </li>
                    <li>
                        If any provision of this Agreement is invalid, illegal
                        or unenforceable, that provision will be severed from
                        this Agreement and all other provisions will remain in
                        full force and effect.
                    </li>
                    <li>
                        This Agreement is governed by and is to be construed in
                        accordance with the laws of British Columbia and the
                        applicable laws of Canada.
                    </li>
                    <li>
                        The Subscriber agrees to the exclusive jurisdiction and
                        venue of the courts of the province of British Columbia,
                        sitting in Victoria, for the hearing of any dispute
                        arising from or related to this Agreement or its subject
                        matter.
                    </li>
                </div>
            </ol>
        </div>
        <template #footer v-if="!isTermsCloseable">
            <div class="button-group">
                <Button
                    label="Cancel and logout"
                    severity="secondary"
                    @click="auth.logout()"
                />

                <Button
                    label="I accept the terms of use"
                    @click="acceptTermsAndConditions()"
                    :is-loading="
                        acceptTermsAndConditionsMutation.isPending.value
                    "
                    :icon="CheckIcon"
                />
            </div>
        </template>
    </Dialog>
</template>

<style lang="scss">
.terms-and-conditions-container {
    a {
        color: var(--link-primary);
    }

    h3,
    p {
        font-size: 0.875rem;
    }

    p,
    li {
        line-height: 1.25rem;
    }

    h3 {
        font-weight: bold;
        margin-top: 1.5rem;
        margin-left: 0;
        padding-left: 0;
    }

    ol {
        padding-left: 1.2rem;
    }

    .terms-list {
        padding-left: 0;
        margin: 0;
        list-style-position: inside;
    }

    li {
        margin-top: 0.5rem;
    }

    .button-group {
        width: 100%;
        gap: 2rem;
        display: flex;
        flex-direction: row;
        .fam-button {
            width: 45%;
            height: 3rem;

            .button-content {
                .button-label {
                    @include type.type-style("body-compact-01");
                }
            }
        }
    }
}
</style>
