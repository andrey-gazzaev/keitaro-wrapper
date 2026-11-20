import type { ChangeEvent, FormEvent } from 'react';
import { Field, Input, Stack } from '@/ui';
import { CreateCampaignActions } from './create-campaign-actions';
import styles from './create-campaign-form.module.css';

const campaignPrefix = import.meta.env.VITE_CAMPAIGN_PREFIX;

const NAME_HINT = `Строка принимается, только если начинается с ${campaignPrefix}.`;
const COUNTRY_HINT = 'Первый поток ловит эту страну и ведёт на Google.';
const OFFER_HINT = 'Второй поток отдаёт остальных на этот оффер, вес 100%.';

type CreateCampaignFormProps = {
  /** Campaign name as typed. Empty when no name is given. */
  readonly name: string;

  /** Country code as typed. Empty when no country is given. */
  readonly country: string;

  /** Offer id as typed. Empty when no id is given. */
  readonly offerId: string;

  /** Message under the name. Empty when the name is accepted. */
  readonly nameError: string;

  /** Message under the country. Empty when the country is accepted. */
  readonly countryError: string;

  /** Message under the offer id. Empty when the offer id is accepted. */
  readonly offerError: string;

  /** Message under the buttons. Empty when the failure belongs to a field or there is none. */
  readonly formError: string;

  /** True while the create is in flight. */
  readonly pending: boolean;

  /** Stores the next name. */
  readonly onName: (event: ChangeEvent<HTMLInputElement>) => void;

  /** Stores the next country. */
  readonly onCountry: (event: ChangeEvent<HTMLInputElement>) => void;

  /** Stores the next offer id. */
  readonly onOfferId: (event: ChangeEvent<HTMLInputElement>) => void;

  /** Sends the draft. */
  readonly onSubmit: (event: FormEvent<HTMLFormElement>) => void;

  /** Closes the dialog. */
  readonly onClose: () => void;
};

/** Name, country, offer id, and the create controls. */
export function CreateCampaignForm({
  name,
  country,
  offerId,
  nameError,
  countryError,
  offerError,
  formError,
  pending,
  onName,
  onCountry,
  onOfferId,
  onSubmit,
  onClose,
}: CreateCampaignFormProps) {
  return (
    <Stack as="form" onSubmit={onSubmit}>
      <Field label="Название" hint={NAME_HINT} error={nameError}>
        <Input value={name} placeholder={`${campaignPrefix}au`} onChange={onName} />
      </Field>
      <Field label="Гео-код" hint={COUNTRY_HINT} error={countryError}>
        <Input value={country} placeholder="AU" onChange={onCountry} />
      </Field>
      <Field label="Id оффера" hint={OFFER_HINT} error={offerError}>
        <Input value={offerId} inputMode="numeric" placeholder="104" onChange={onOfferId} />
      </Field>

      <CreateCampaignActions pending={pending} onClose={onClose} />

      {formError !== '' ? <p className={styles.error}>{formError}</p> : null}
    </Stack>
  );
}
