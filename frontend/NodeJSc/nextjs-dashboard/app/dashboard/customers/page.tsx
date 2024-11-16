import Image from 'next/image';


export default function Page() {
  return <>
  <Image
      src="/plot.png"
      width={1000}
      height={760}
      className="hidden md:block"
      alt="Screenshots of the dashboard project showing desktop version"
    />
  </>
}

