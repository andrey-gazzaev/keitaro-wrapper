import { memo, useCallback, useState, type ChangeEvent, type FormEvent } from 'react';
import { mapCampaignFormError } from '@/mappers';
import { useCreateCampaign } from '@/queries';
import { Modal } from '@/ui';
import { positiveOfferId } from '@/utils';
import { CreateCampaignForm } from './create-campaign-form';

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

  const failure = mapCampaignFormError(createCampaign.isError ? createCampaign.error : null);
  const succeeded = createCampaign.isSuccess && createCampaign.data !== undefined;

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

  return (
    <>
      {succeeded && createCampaign.data ? <p className="status">Кампания «{createCampaign.data.name}» создана.</p> : null}

      {open ? (
        <Modal title="Новая кампания" description={DIALOG_DESCRIPTION} onClose={onClose}>
          <CreateCampaignForm
            name={name}
            country={country}
            offerId={offerId}
            nameError={failure.name}
            countryError={failure.country}
            offerError={failure.offerId}
            formError={failure.form}
            pending={createCampaign.isPending}
            onName={onName}
            onCountry={onCountry}
            onOfferId={onOfferId}
            onSubmit={submit}
            onClose={onClose}
          />
        </Modal>
      ) : null}
    </>
  );
});
