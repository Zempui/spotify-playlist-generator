'use client'

import { useFormState, useFormStatus } from "react-dom";
import { loginAction, searchAction } from "./serverComponents";
import { useEffect, useState } from "react";

const SubmitButton = ({id, defaultText, pendingText}: {id: string, defaultText: string, pendingText: string}) => {
	const { pending } = useFormStatus();

	return (
		<button hidden={defaultText === ''} id={id} type='submit' aria-disabled={pending} disabled={pending}>
			{pending && pendingText || !pending && defaultText}
		</button>
	)
}

export default function ClientComponent({loggedIn}: {loggedIn: boolean}) {
  const [loginState, formLoginAction] = useFormState(loginAction, {});
  const [searchState, formSearchAction] = useFormState(searchAction, {error: '', object: [], status: 0});
  const [artistsFound, setArtistsFound] = useState(false)
  const [inputValue, setInputValue] = useState('');

  const handleInputChange = (event: any) => {
    setInputValue(event.target.value);
    if (event.target.value === '') {
      searchState.object = []
    }
  };

  const handleClearButtonClick = () => {
    setInputValue('');
    searchState.object = []
  };

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (inputValue !== '') {
        document.getElementById('searchButton')?.click();
      }
    }, 500);
  
    return () => clearTimeout(timeoutId); // Limpiar el timeout en cada renderización
  }, [inputValue]);

  useEffect(() => {
    setArtistsFound(searchState.object.length !== 0)
  }, [searchState.object])

  return (
<div className="max-w-lg mx-auto">
  {!loggedIn && (
    <form action={formLoginAction} className="mb-4">
      <SubmitButton id='loginButton' defaultText="Inicia sesión con Spotify" pendingText="Serás redirigido en breve..." />
    </form>
  )}

  {loggedIn && (
    <form action={formSearchAction} className="mb-4">
      <div className="flex items-center border rounded-md overflow-hidden">
        <input
          autoComplete="off"
          id="query"
          name="query"
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          className="py-2 px-4 flex-grow focus:outline-none"
          placeholder="Buscar..."
        />
        {inputValue && (
          <button
            onClick={handleClearButtonClick}
            className="bg-gray-300 text-gray-600 px-4 py-2 rounded focus:outline-none hover:bg-gray-400"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        )}
      </div>

      <SubmitButton id='searchButton' defaultText="" pendingText="" />
    </form>
  )}

  {artistsFound &&
    searchState.object.map((value: any) => (
      <div key={value.id} className="flex items-center bg-white shadow-md rounded-lg p-4 hover:shadow-lg cursor-pointer mb-4">
        <img src={value.image.url} alt={value.name} className="h-16 w-16 rounded-full mr-4" />
        <p className="text-lg">{value.name}</p>
      </div>
    ))
  }
</div>

  );
}
