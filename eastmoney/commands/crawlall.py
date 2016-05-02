from scrapy.command import ScrapyCommand  
from scrapy.crawler import Crawler
from scrapy.crawler import CrawlerProcess
from scrapy.utils.conf import arglist_to_dict
import os
import sys
from importlib import import_module
from scrapy.utils.spider import iter_spider_classes

def _import_file(filepath):
    abspath = os.path.abspath(filepath)
    dirname, file = os.path.split(abspath)
    fname, fext = os.path.splitext(file)
    if fext != '.py':
        raise ValueError("Not a Python source file: %s" % abspath)
    if dirname:
        sys.path = [dirname] + sys.path
    try:
        module = import_module(fname)
    finally:
        if dirname:
            sys.path.pop(0)
    return module
class Command(ScrapyCommand):
    requires_project = False
    def syntax(self):  
        return '[options]'  
    def short_desc(self):  
        return 'Runs all of the spiders'  
    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_option("-a", dest="spargs", action="append", default=[], metavar="NAME=VALUE",help="set spider argument (may be repeated)")
        parser.add_option("-o", "--output", metavar="FILE",help="dump scraped items into FILE (use - for stdout)")
        parser.add_option("-t", "--output-format", metavar="FORMAT",help="format to use for dumping items with -o")
    def process_options(self, args, opts):
        ScrapyCommand.process_options(self, args, opts)
        try:
            opts.spargs = arglist_to_dict(opts.spargs)
        except ValueError:
            raise UsageError("Invalid -a value, use -a NAME=VALUE", print_help=False)
        if opts.output:
            if opts.output == '-':
                self.settings.set('FEED_URI', 'stdout:', priority='cmdline')
            else:
                self.settings.set('FEED_URI', opts.output, priority='cmdline')
            valid_output_formats = (
                list(self.settings.getdict('FEED_EXPORTERS').keys()) +
                list(self.settings.getdict('FEED_EXPORTERS_BASE').keys())
            )
            if not opts.output_format:
                opts.output_format = os.path.splitext(opts.output)[1].replace(".", "")
            if opts.output_format not in valid_output_formats:
                raise UsageError("Unrecognized output format '%s', set one"
                                 " using the '-t' switch or as a file extension"
                                 " from the supported list %s" % (opts.output_format,
                                                                  tuple(valid_output_formats)))
            self.settings.set('FEED_FORMAT', opts.output_format, priority='cmdline')
    def run(self, args, opts):
        #settings = get_project_settings()
        #spider_loader = self.crawler_process.spider_loader
        crawler = self.crawler_process.create_crawler()
        names = crawler.spiders.list()
        spclasses = []
        for spidername in names:
            crawler = self.crawler_process.create_crawler()
            module = _import_file("./eastmoney/spiders/"+spidername+"_spider.py")
            #spclasses = spclasses+list(iter_spider_classes(module))
            spider = list(iter_spider_classes(module)).pop()(**opts.spargs)
            crawler.crawl(spider)
            self.crawler_process.start()
            crawler._spider = None