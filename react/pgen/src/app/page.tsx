'use client'

import { useFormState, useFormStatus } from "react-dom";
import { loginAction } from "./serverComponents";

const SubmitButton = ({defaultText, pendingText}: {defaultText: string, pendingText: string}) => {
	const { pending } = useFormStatus();

	return (
		<button type='submit' aria-disabled={pending} disabled={pending}>
			{pending && pendingText || !pending && defaultText}
		</button>
	)
}

export default function Home() {
  const [state, formAction] = useFormState(loginAction, {});
  return (
    <>
      <form action={formAction}>
        <SubmitButton defaultText="Inicia sesión con spotify" pendingText="Serás redirigido en breve..."/>
      </form>
    </>
  );
}
