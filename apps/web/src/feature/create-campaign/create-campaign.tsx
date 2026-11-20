import { memo, useCallback, useMemo, useState, type ChangeEvent, type FormEvent } from 'react';
import axios from 'axios';
import { useCreateCampaign } from '@/queries';
import { Button, Field, Modal, Stack } from '@/ui';
import styles from './create-campaign.module.css';

const campaignPrefix = import.meta.env.VITE_CAMPAIGN_PREFIX;

const NAME_HINT = `Строка принимается, только если начинается с ${campaignPrefix}.`;
const COUNTRY_HINT = 'Первый поток ловит эту страну и ведёт на Google.';
const OFFER_HINT = 'Второй поток отдаёт остальных на этот оффер, вес 100%.';
const DIALOG_DESCRIPTION = 'Название, гео-код и id оффера. Домен, группа и источник проставятся из Keitaro.';

type CreateCampaignProps = {
  /** True while the dialog is open. */
  readonly open: boolean;

  /** Closes the dialog. */
  readonly onClose: () => void;
};

/** Dialog that creates one campaign. */
export const CreateCampaign = memo(function CreateCampaign({ open, onClose }: CreateCampaignProps) {
  const [name, setName] = useState('');
  const [country, setCountry] = useState('');
  const [offerId, setOfferId] = useState('');
  const createCampaign = useCreateCampaign();

  const onName = useCallback((event: ChangeEvent<HTMLInputElement>) => {
    setName(event.target.value);
  }, []);

  const onCountry = useCallback((event: ChangeEvent<HTMLInputElement>) => {
    setCountry(event.target.value);
  }, []);

  const onOfferId = useCallback((event: ChangeEvent<HTMLInputElement>) => {
    setOfferId(event.target.value);
  }, []);

  const submit = useCallback(
    (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();

      const trimmedName = name.trim();
      const trimmedCountry = country.trim();
      const parsedOfferId = positiveOfferId(offerId);

      if (trimmedName === '' || trimmedCountry === '' || parsedOfferId === null) {
        return;
      }

      createCampaign.mutate(
        { name: trimmedName, country: trimmedCountry, offerId: parsedOfferId },
        { onSuccess: () => onClose() },
      );
    },
    [name, country, offerId, createCampaign.mutate, onClose],
  );

  const errorText = createCampaign.isError ? createFailure(createCampaign.error) : '';
  const pending = createCampaign.isPending;

  const nameInput = useMemo(
    () => <input value={name} placeholder={`${campaignPrefix}au`} onChange={onName} />,
    [name, onName],
  );

  const countryInput = useMemo(
    () => <input value={country} placeholder="AU" onChange={onCountry} />,
    [country, onCountry],
  );

  const offerInput = useMemo(
    () => <input value={offerId} inputMode="numeric" placeholder="104" onChange={onOfferId} />,
    [offerId, onOfferId],
  );

  const actions = useMemo(
    () => (
      <div className={styles.actions}>
        <Button type="button" variant="secondary" onClick={onClose}>
          Отмена
        </Button>
        <Button type="submit" variant="primary" disabled={pending}>
          Создать
        </Button>
      </div>
    ),
    [onClose, pending],
  );

  const form = useMemo(
    () => (
      <Stack as="form" onSubmit={submit}>
        <Field label="Название" hint={NAME_HINT}>
          {nameInput}
        </Field>
        <Field label="Гео-код" hint={COUNTRY_HINT}>
          {countryInput}
        </Field>
        <Field label="Id оффера" hint={OFFER_HINT}>
          {offerInput}
        </Field>
        {actions}
        {errorText !== '' ? <p className={styles.error}>{errorText}</p> : null}
      </Stack>
    ),
    [nameInput, countryInput, offerInput, actions, submit, errorText],
  );

  const succeeded = createCampaign.isSuccess && createCampaign.data !== undefined;

  return (
    <>
      {succeeded && createCampaign.data ? <p className="status">Кампания «{createCampaign.data.name}» создана.</p> : null}

      {open ? (
        <Modal title="Новая кампания" description={DIALOG_DESCRIPTION} onClose={onClose}>
          {form}
        </Modal>
      ) : null}
    </>
  );
});

function positiveOfferId(value: string): number | null {
  const trimmed = value.trim();

  if (!/^[1-9]\d*$/.test(trimmed)) {
    return null;
  }

  return Number(trimmed);
}

function createFailure(error: unknown): string {
  if (!axios.isAxiosError(error)) {
    return 'Keitaro не ответил.';
  }

  if (error.response?.status === 422) {
    return 'Проверьте название, страну и id оффера.';
  }

  if (error.response?.status === 409) {
    return 'В Keitaro нет домена, группы или источника.';
  }

  if (error.response?.status === 404) {
    return 'Оффер не найден.';
  }

  if (error.response?.status === 503) {
    return 'API Keitaro не настроен.';
  }

  return 'Keitaro не ответил.';
}
