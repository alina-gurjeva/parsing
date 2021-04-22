from parse_5ka import Parse5ka, get_save_path
import time


class ParseCat5ka(Parse5ka):
    """
    dedicated to collect products with categories
    """
    def _get_categories(self):
        """
        gets list with categories of products
        """
        url_categories = 'https://5ka.ru/api/v2/categories/'
        response = self._get_response(url_categories, headers=self.headers, params=self.params)
        r = response.json()
        self.categories_codes = {r[i]['parent_group_code']: r[i]['parent_group_name'] for i in range(len(r))}

    def _parse(self, url: str):
        """
        gets products for all categories

        :param url: start url
        :return category_dict: dict with results
        """
        start_url = url
        for item in self.categories_codes.items():
            category_dict = {'code': item[0], 'name': item[1], 'products': []}
            self.params['categories'] = int(item[0])
            while True:
                time.sleep(0.5)
                response = self._get_response(url, headers=self.headers, params=self.params)
                data = response.json()
                url = data["next"]
                print(data["results"])
                category_dict['products'].extend(data["results"])
                if not url:
                    url = start_url
                    break
            yield category_dict

    def run(self):
        """
        gets categories, then runs overwrote parent run func (saves files for every yield result)
        """
        self._get_categories()
        for category_dict in self._parse(self.star_url):
            file_path = self.save_path.joinpath(f"{category_dict['code']}.json")
            self._save(category_dict, file_path)


if __name__ == "__main__":
    save_path = get_save_path("products")
    url = "https://5ka.ru/api/v2/special_offers/"
    parser = ParseCat5ka(url, save_path)
    parser.run()

