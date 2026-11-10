"""Offline migration CLI. It never changes source plugins or their activation state."""
import argparse,importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('third_party_migration_source',ROOT/'__init__.py',submodule_search_locations=[str(ROOT)])
package=importlib.util.module_from_spec(spec);sys.modules[spec.name]=package;spec.loader.exec_module(package)
from third_party_migration_source.migration import apply,preview
from third_party_migration_source.core.store import Store

def main():
 parser=argparse.ArgumentParser(description='将旧 B站/小黑盒数据导入独立暂存目录，保留全部原文件。')
 parser.add_argument('--source-data',type=Path,required=True)
 parser.add_argument('--target-data',type=Path)
 parser.add_argument('--apply',action='store_true')
 parser.add_argument('--legacy-stopped',action='store_true',help='确认已停止 AstrBot 和旧插件写入后使用')
 args=parser.parse_args()
 if not args.apply:
  print(json.dumps(preview(args.source_data),ensure_ascii=False,indent=2));return
 if args.target_data is None:parser.error('--apply requires --target-data')
 result=apply(args.source_data,args.target_data,source_stopped=args.legacy_stopped)
 Store(args.target_data/'platforms.sqlite3').set_setting('deployment',{'schema':1,'verified':True,'mode':'offline_migration','legacy_retained':True})
 print(json.dumps({'status':'imported_disabled','summary':result,'next':'Review imported-config.json privately; copy it into AstrBot config and the staged data into this plugin data directory. Keep old plugins and old xiaoheihe connection disabled. Then check login/model readiness before enabling.'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
