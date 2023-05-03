import scrape from 'website-scraper';

try {
  const options = {
    urls: process.argv[2],
    directory: process.argv[3]
  };

  // with async/await
  const result = await scrape(options);

  // with promise
  scrape(options).then((result) => {});

} catch (error) {

}